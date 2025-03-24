import requests
import time
import json
import logging
import string
from typing import Literal
from urllib.parse import quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("autocomplete_extraction.log"),
        logging.StreamHandler(),
    ],
)


class AutocompleteExtractor:
    def __init__(self, base_url: str, max_results: int, charlist: str, version: Literal["v1", "v2", "v3"]):
        self.base_url = base_url
        self.max_results = max_results
        self.discovered_names = set()
        self.request_count = 0
        self.charlist = sorted(charlist)
        self.version = version

    def get_autocomplete_suggestions(self, query: str):
        query = quote(query)
        url = f"{self.base_url}/{self.version}/autocomplete?query={query}&max_results={self.max_results}"

        try:
            response = requests.get(url)
            self.request_count += 1

            # Handle rate limiting
            if response.status_code == 429:
                logging.warning(f"Rate limited. Sleeping for 10 seconds.")
                time.sleep(10)
                return self.get_autocomplete_suggestions(query)

            if response.status_code != 200:
                logging.error(f"Error status code: {response.status_code}")
                time.sleep(1)
                return []

            data = response.json()

            if "results" in data and isinstance(data["results"], list):
                suggestions: list = data["results"]
                logging.info(
                    f"Query '{query}' returned {len(suggestions)} suggestions. Current total: {len(self.discovered_names)}"
                )

                if suggestions and len(suggestions) > 0:
                    logging.debug(
                        f"First few: {suggestions[:3]}, Last: {suggestions[-1]}"
                    )

                return suggestions
            else:
                logging.warning(f"Unexpected response format: {data.keys()}")
                return []

        except Exception as e:
            logging.error(f"Error querying '{query}': {str(e)}")
            return []

    def crawl_autocomplete(self):
        logging.info(f"Starting extraction with max_results={self.max_results}")
        start_time = time.time()

        # Start with single letters
        for first_letter in self.charlist:
            if first_letter == " ":
                continue # Skip space
            self.crawl_prefix(first_letter)

        elapsed_time = time.time() - start_time
        logging.info(f"Extraction completed in {elapsed_time:.2f} seconds")
        logging.info(f"Total API requests: {self.request_count}")
        logging.info(f"Total names discovered: {len(self.discovered_names)}")

        return self.discovered_names

    def crawl_prefix(self, prefix: str):
        """
        Crawl a specific prefix and its subprefixes systematically.
        If we hit the max_results limit, try all possible next characters.
        """
        logging.info(f"Processing prefix: '{prefix}'")

        suggestions = self.get_autocomplete_suggestions(prefix)

        # Add all suggestions to our discovered names
        for name in suggestions:
            self.discovered_names.add(name)

        # If we got exactly max_results, we need to explore further
        if len(suggestions) == self.max_results:
            # Try all possible next characters (a-z)
            next_char = suggestions[-1][len(prefix)]
            ind = self.charlist.index(next_char)
            for next_char in self.charlist[ind:]:
                if next_char == " ":
                    continue
                next_prefix = prefix + next_char
                self.crawl_prefix(next_prefix)

        # time.sleep(self.rate_limit_delay)

    def save_results(self, output_file="discovered_names.json"):
        results = {
            "total_requests": self.request_count,
            "total_names": len(self.discovered_names),
            "names": sorted(list(self.discovered_names)),
        }

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        logging.info(f"Results saved to {output_file}")


def main():
    extractor = AutocompleteExtractor(
        "http://35.200.185.69:8000", 50, string.ascii_lowercase, "v1"
    )

    all_names = extractor.crawl_autocomplete()
    extractor.save_results()

    print(f"Extraction complete. Found {len(all_names)} names.")
    print(f"Made {extractor.request_count} API requests.")


if __name__ == "__main__":
    main()
