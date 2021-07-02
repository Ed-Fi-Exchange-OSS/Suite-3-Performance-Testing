# Ed-Fi-X-ODS-Performance

Performance testing framework for the Ed-Fi ODS technical suite 3

## Installation

1. If you don't already have [Git for Windows](https://gitforwindows.org/) on
   your system, install it.
1. Choose a parent directory (e.g., `C:\dev`) to house this repository and
   either clone this repository there (`cd` to that directory and run `git clone
   https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing.git`), or use the "Clone
   or Download" link above to download a ZIP file and unzip it into that
   directory.  Either method will create an `Suite-3-Performance-Testing` directory
   containing the repository.
1. Checkout the right tag for the version you wish to test against, e.g.
   `git checkout 3.0.0` or `git checkout 3.1.0`.

### Installing Test Runner Prerequisites

See `Administration\install-test-runner-prerequisites.ps1`. This script installs
and sets up all prerequisites. **Run this script in an Administrator PowerShell
prompt.** The script installs and sets up the following:

* Chocolately, the Windows package installer
* Python 3.6.7
* Python's 'virtualenv' sandboxing tool
* Creates an EDFI_PERFORMANCE virtual environment (which will contain all of the
  installed python dependencies for this project; located at `C:\virtualenv`)

## Usage

### Running a locust test with performance metrics and logs (Recommended)

1. Start the local Ed-Fi ODS API.  (See
   [here](https://techdocs.ed-fi.org/display/ODSAPIS3V520/Getting+Started+-+Source+Code+Installation)
   for installation and invocation instructions.)
1. Inspect `locust-config.json` to verify the configuration values are correct
   for your local environment.
1. Open a command prompt window and cd to the root to the repository. (`cd
   C:\dev\Suite-3-Performance-Testing`)
1. Run the following command to run the standard volume test: `run-tests Volume`
1. To run a pipeclean, soak, stress, or change query test, you can replace
   `Volume` with either `Pipeclean`, `Soak`, `Stress`, or `ChangeQuery`, respectively.
1. Once the test finishes, you can look inside the TestResults directory, which
   will be located at the root of the repository to see log entries, performance
   metrics, and locust results.

### Running a specific locust test

1. Start the local Ed-Fi ODS API.  (See
   [here](https://techdocs.ed-fi.org/display/ODSAPIS3V520/Getting+Started+-+Source+Code+Installation)
   for installation and invocation instructions.)
1. Open a command prompt window and cd to the root of the repo. (`cd
   C:\dev\Suite-3-Performance-Testing`)
1. Run `C:\virtualenv\EDFI_PERFORMANCE\Scripts\activate.bat` to enter the
   virtual environment. (If this command cannot be found, refer to 'Installing
   Test Runner Prerequisites' above)
1. If this is your first time running locust tests, install locust and other
   packages by running `pip install -r requirements.txt`.
1. For more fine-grained control over the scenarios, you can use the `locust`
   command.  For example, to run just the School and Student volume tests with
   20 clients, use `locust -f volume_tests.py -c 20 --no-web SchoolVolumeTest
   StudentVolumeTest`.  Use `locust --help` for more information on how to use
   Locust itself.
1. To run pipeclean tests, use locust with `-f pipeclean_tests.py`.  Individual
   resources can be tested similarly to volume tests, e.g. `locust -f
   pipeclean_tests.py -c 1 --no-web SchoolPipecleanTest StudentPipecleanTest`.
   We recommend running pipeclean tests with a single client (`-c 1`) so each
   endpoint is hit once (except for dependencies, which will be created and
   deleted as needed).
1. To run change query tests, use locust with `-f change_query_tests.py`.  Individual
   resources can be tested similarly to volume tests, e.g. `locust -f
   change_query_tests.py -c 1 --no-web StaffChangeQueryTest StudentChangeQueryTest`.
   We recommend running change query tests with a single client (`-c 1`) so each
   resource's changes are fetched once.

### Customization

The following Locust settings for local development are in `locust-config.json`:

* `"host"`: change this to have Locust test against an ODS installation at
  another URL.  Enter the base URL of the installation, e.g.
  `https://staging.ed-fi.org/ods-1234/`.
* `"client_id"`: the client key to authenticate to the ODS installation being
  tested.
* `"client_secret"`: the  client secret corresponding to the client key.
* `"delete_resources"`: change this to "false" when you don't want resources to
  be deleted. This is "true" by default
* `"fail_deliberately"`: change this to "true" when you want some volume test
  scenarios to fail deliberately.
* `"database_server"`: this will always be 'localhost' when testing locally
* `"web_server"`: this will always be 'localhost' when testing locally
* `"log_file_path"`: this path points to the folder where the ODS API logs are
  stored.
* `"sql_backup_path"`: this path points to the folder where the SQL Server .BAK
  files are stored
* `"sql_data_path"`: this path points to the folder where the .ldf and .mdf
  files are written to when the database is restored
* `"database_name"`: this is the name of the database that is being overwritten
  and restored on
* `"backup_filename"`: this is the .BAK file that is going to be restored
* `"restore_database"`: change this to "true" if you would like the database to
  be restored when testing. This is "false" by default