# Paging Volume Test

Provides data out performance metrics for the ODS / AP aimed at analysis of bottlenecks, and providing recommendations for server sizing for representative agency simulation sizes.

## Getting Started

1. Requires Python 3.6+ and Poetry.
1. Install required Python packages:

   ```bash
   poetry install
   ```

## Running the Tool
For detailed help, execute `poetry run python edfi_paging_test -h`.

Sample call using full integrated security, loading from the sample files
directory:

```bash
poetry run python edfi_paging_test --server localhost --dbname lms_toolkit --useintegratedsecurity
```

## Developer Notes
Supported parameters:

|Command Line Argument        | Required            | Description                                                                                  |
| --------------------------- | ------------------- | ---------------------------------------------------------------------------------------------| 
| `-b` or `--baseUrl`         | yes (no default)    | ​The base url used to derived api, metadata, oauth, and dependency urls (e.g., http://server).|	       
| `-k` or `--key`             | yes (no default)    | The web API OAuth key                                                                        |
| `-s` or `--secret`          | yes (no default)    | The web API OAuth secret                                                                     | 
| `-c` or `--connectionLimit` | no (default: 4)     | Maximum concurrent connections to api                                                        |
| `-o` or `--output`          | no default: out)    | Directory for writing results                                                                | 
| `-t` or `--contentType`     | no (default: csv)   | CSV or JSON                                                                                  | 
| `-r` or `--retries`         | no (default: 5)     | Number of time to retry in case of error                                                     | 
| `-l` or `--resourceList`    | no (no default)     | (Optional) List of resources to test  - if not provided, all resources will be retrieved     |
| `-p` or `--pageSize`        | no (default: 100)   | The page size to request. Max: 500.                                                          | 



### Dev Operations

1. Style check: `poetry run flake8`
1. Static typing check: `poetry run mypy .`
1. Run unit tests: `poetry run pytest`
1. Run unit tests with code coverage: `poetry run coverage run -m pytest tests`
1. View code coverage: `poetry run coverage report`