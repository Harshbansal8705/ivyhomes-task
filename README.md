# Autocomplete Name Extractor

This project is a solution to extract all possible names from an undocumented autocomplete API running at `http://35.200.185.69:8000`. The goal was to systematically discover the API's behavior, handle its constraints (e.g., rate limiting), and efficiently extract all available names.

## Problem Statement

The task required:
- Writing a program to extract all names from the autocomplete API.
- Discovering the API's behavior through exploration, as no official documentation was provided.
- Handling constraints like rate limiting and undocumented parameters.
- Documenting findings and the problem-solving process.

The provided starting point was the endpoint `/v1/autocomplete?query=`.

## Approach

### API Exploration
I began by testing the known endpoint and systematically explored its behavior:
1. **Root Endpoint (`/`)**: Returns a message suggesting to try different endpoints and API versions.
2. **Autocomplete Endpoint (`/v1/autocomplete?query=`)**
   - Accepts a `query` parameter.
   - Returns a JSON response with `version`, `count`, and `results` (a list of suggestions).
   - Empty query (`query=`) returns the same 10 results as `query=a`.
3. **API Versions**: Discovered `v1`, `v2`, and `v3` endpoints with different behaviors.
4. **Parameters**: Identified `max_results` as an additional parameter controlling the number of returned suggestions.
5. **Rate Limits**: Encountered rate limits of 100, 50, and 80 requests per minute for `v1`, `v2`, and `v3`, respectively.

### Key Findings
- **API Versions**:
  - `v1`: Default 10 results, max `max_results=50`.
  - `v2`: Default 12 results, max `max_results=75`.
  - `v3`: Default 15 results, max `max_results=100`.
- **Rate Limits**:
  - `v1`: 100 requests/minute.
  - `v2`: 50 requests/minute.
  - `v3`: 80 requests/minute.
  - Exceeding the limit returns a 429 status code with `{"detail": "X per 1 minute"}`.
- **Parameter Behavior**:
  - `limit`, `count`, and `offset` parameters had no effect.
  - `max_results` caps at 50, 75, and 100 for `v1`, `v2`, and `v3`, respectively.
- **Response Consistency**:
  - Suggestions vary by version, suggesting different datasets or generation logic.
  - When `max_results` is hit, the API truncates results, requiring deeper prefix exploration.

### Solution Strategy
1. **Prefix Crawling**: Recursively query prefixes (e.g., `a`, `aa`, `ab`, etc.) to uncover all names.
2. **Pagination Handling**: Use `max_results` to maximize results per request. If the response hits `max_results`, explore the next character in the alphabet.
3. **Rate Limit Management**: Implement retries with a 10-second delay on 429 status codes.
4. **Efficiency**: Store unique names in a set to avoid duplicates and log progress for debugging.

### Challenges and Solutions
- **Undocumented API**: Reverse-engineered behavior through trial and error.
- **Rate Limiting**: Added delays and retries to respect limits.
- **Incomplete Results**: Used recursive prefix crawling when `max_results` was hit.
- **Scalability**: Focused on `v1` initially but designed the code to support `v2` and `v3`.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Harshbansal8705/ivyhomes-task
   cd ivyhomes-task
   ```
2. Install dependencies:
   ```
   pip install requests
   ```
3. Ensure Python 3.7+ is installed.

## Usage

Run the script to extract names from the `v1` endpoint:
```
python autocomplete_extractor.py
```

### Customization
- Modify the `AutocompleteExtractor` initialization in `main()` to target different versions or character sets:
  ```python
  extractor = AutocompleteExtractor(
      base_url="http://35.200.185.69:8000",
      max_results=50,  # Adjust based on version (50 for v1, 75 for v2, 100 for v3)
      charlist=string.ascii_lowercase,  # Character set to explore
      version="v1"  # Options: "v1", "v2", "v3"
  )
  ```

### Output
- Results are saved to `discovered_names.json` with:
  - `total_requests`: Number of API calls made.
  - `total_names`: Number of unique names found.
  - `names`: Sorted list of discovered names.
- Logs are written to `autocomplete_extraction.log`.


## Results

Below are the results from sample runs on each API version. The extraction was performed with the maximum allowed `max_results` for each version to optimize efficiency. Note that actual values depend on the API's dataset size, network conditions, and rate limit enforcement during the run.

| API Version | `max_results` | Rate Limit (req/min) | Total Requests | Total Names |
|-------------|---------------|----------------------|----------------|-------------|
| `v1`        | 50            | 100                  | 1726           | 18,632      |
| `v2`        | 75            | 50                   | 2176           | 13730       |
| `v3`        | 100           | 80                   | 2636           | 12318       |

### Notes
- **Total Requests**: Number of API calls made to extract all names. Varies based on the dataset size and how often `max_results` is hit, triggering deeper prefix crawling.
- **Total Names**: Unique names discovered. The differences across versions suggest distinct datasets or generation logic.

These numbers vary based on the API's dataset size and rate limit enforcement.

## Code Structure
- **`AutocompleteExtractor` Class**:
  - `__init__`: Initializes API settings.
  - `get_autocomplete_suggestions`: Handles API requests and rate limiting.
  - `crawl_autocomplete`: Main extraction logic.
  - `crawl_prefix`: Recursive prefix exploration.
  - `save_results`: Exports results to JSON.
- **Logging**: Tracks progress and errors.
- **Typing**: Uses type hints for clarity.

## Tools and Scripts
- **Main Script**: `autocomplete_extractor.py` contains the full solution.
- **Logging**: Logs saved to `autocomplete_extraction.log` for debugging.

## Future Improvements
- **Parallel Requests**: Use asyncio to parallelize requests within rate limits.
- **Dynamic Rate Limiting**: Adjust sleep times based on remaining quota.
- **Multi-Version Support**: Run extraction across all versions concurrently.
- **Incremental Saving**: Save progress periodically to resume on failure.

## Submission Details
- **Code**: `autocomplete_extractor.py`
- **Documentation**: This `README.md`
- **Logs**: `autocomplete_extraction.log`
- **Output**: `discovered_names.json`
