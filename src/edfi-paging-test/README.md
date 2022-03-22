# Paging Volume Test

Provides data out performance metrics for the ODS / AP aimed at analysis of
bottlenecks, and providing recommendations for server sizing for representative
agency simulation sizes.

## Getting Started

1. Requires Python 3.9+ and Poetry.
1. Install required Python packages:

   ```bash
   poetry install
   ```

## Running the Tool

For detailed help, execute `poetry run python edfi_paging_test -h`.

Sample call using full integrated security, loading from the sample files
directory:

```bash
poetry run python edfi_paging_test -b "http://localhost:54746" -k "testkey" -s "testsecret" -l "resource1" "resource2"
```

## Developer Notes

Supported arguments:

| Command Line Argument       | Required           | Description                                                                                   |
| --------------------------- | ------------------ | --------------------------------------------------------------------------------------------- |
| `-b` or `--baseUrl`         | yes (no default)   | ​The base url used to derived api, metadata, oauth, and dependency urls (e.g., http://server)  |
| `-k` or `--key`             | yes (no default)   | The web API OAuth key                                                                         |
| `-s` or `--secret`          | yes (no default)   | The web API OAuth secret                                                                      |
| `-c` or `--connectionLimit` | no (default: 4)    | Maximum concurrent connections to api                                                         |
| `-o` or `--output`          | no default: out)   | Directory for writing results                                                                 |
| `-t` or `--contentType`     | no (default: csv)  | Output file content type: CSV, JSON                                                           |
| `-r` or `--resourceList`    | no (no default)    | (Optional) List of resources to test  - if not provided, all resources will be retrieved      |
| `-p` or `--pageSize`        | no (default: 100)  | The page size to request. Max: 500.                                                           |
| `-l` or `--logLevel`        | no (default: INFO) | Override the console output log level: VERBOSE, DEBUG, INFO, WARN, ERROR                      |

Each argument can also be set by environment variable, or by using as `.env`
file. See [.env.example](edfi_paging_test/.env.example). Arguments provided at
the command line override any arguments provided by environment variable.

### Dev Operations

1. Style check: `poetry run flake8`
1. Static typing check: `poetry run mypy .`
1. Run unit tests: `poetry run pytest`
1. Run unit tests with code coverage: `poetry run coverage run -m pytest tests`
1. View code coverage: `poetry run coverage report`
