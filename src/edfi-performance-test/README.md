# Performance Tests

Provides performance metrics for the ODS / API  SIS Certification endpoints aimed at analysis of
bottlenecks, and providing recommendations for server sizing for representative
agency simulation sizes.

## Getting Started

1. Requires Python 3.9+ and Poetry.
1. Install required Python packages:

   ```bash
   poetry install
   ```

## Running the Tool

For detailed help, execute `poetry run python edfi_performance_test -h`.

Sample call using full integrated security, loading from the sample files
directory:

```bash
poetry run python edfi_performance_test -b "https://localhost:54746" -k "testkey" -s "testsecret"
```

Test failure ratio is monitored throughout and run is stopped if more than 50% of the
tests experience failures.

### Supported arguments

| Command Line Argument                | Required                             | Description                                                                                                    |
| ------------------------------------ | ------------------------------------ | ---------------------------------------------------------------------------------------------------------------|
| `-b` or `--baseUrl`                  | yes (no default)                     | ​The base url used to derived api, metadata, oauth, and dependency urls (e.g., http://server)                   |
| `-k` or `--key`                      | yes (no default)                     | The web API OAuth key                                                                                          |
| `-s` or `--secret`                   | yes (no default)                     | The web API OAuth secret                                                                                       |
| `-i` or `--ignoreCertificateErrors`  | no (default: false)                  | Ignore certificate errors                                                                                      |
| `-d` or `--deleteResources`          | no (default: true)                   | Delete resources during test run                                                                               |
| `-f` or `--failDeliberately`         | no (default: true)                   | Deliberately introduce requests that result in failure                                                         |
| `-c` or `--clientCount`              | no (default: 1000)                   | Total number of users spawned by locust tests                                                                  |
| `-r` or `--spawnRate`                | no (default: 25)                     | Number of users spawned by locust tests per second                                                             |
| `-t` or `--runTimeInMinutes`         | no (default: 30)                     | Test Run Time                                                                                                  |
| `-g` or `--runInDebugMode  `         | no (default: false)                  | Runs tests in single user mode. When set to true, clientCount, spawnRate and runTimeInMinutes will be ignored  |
| `-o` or `--output`                   | no (default: out)                    | Directory for writing results                                                                                  |
| `-l` or `--logLevel`                 | no (default: INFO)                   | Override the console output log level: VERBOSE, DEBUG, INFO, WARN, ERROR                                       |


Each argument can also be set by environment variable, or by using as `.env`
file. See [.env.example](edfi_performance_test/.env.example). Arguments provided at
the command line override any arguments provided by environment variable.

### Dev Operations

1. Style check: `poetry run flake8`
2. Static typing check: `poetry run mypy .`
3. Run unit tests: `poetry run pytest`
4. Run unit tests with code coverage: `poetry run coverage run -m pytest tests`
5. View code coverage: `poetry run coverage report`
