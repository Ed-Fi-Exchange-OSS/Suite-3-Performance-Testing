# User Guide for the Suite 3 Performance Test Kit

- [User Guide for the Suite 3 Performance Test Kit](#user-guide-for-the-suite-3-performance-test-kit)
  - [Pre-requisites](#pre-requisites)
  - [Getting Started](#getting-started)
  - [Paging Tests](#paging-tests)
    - [Paging Configuration](#paging-configuration)
  - [Running the Paging Volume Tests](#running-the-paging-volume-tests)
  - [SIS Certification Performance Tests](#sis-certification-performance-tests)
    - [SIS Certification Configuration](#sis-certification-configuration)
    - [Running the SIS Certification Performance Tests](#running-the-sis-certification-performance-tests)
      - [Pipeclean](#pipeclean)
      - [Volume](#volume)
      - [Stress](#stress)
      - [Soak](#soak)
      - [Change Queries](#change-queries)
  - [Troubleshooting](#troubleshooting)

## Pre-requisites

The Python, Poetry, and Powershell requirements below can be installed
with the help of the scripts in the [eng directory](../eng). To isolate this Python environment to the repository, it's recommended to run the scripts from the repository's root.

```bash
./eng/install-test-runner-prerequisites.ps1
```  

* Ed-Fi ODS/API Suite 3, version 5.x and 6.x
  * ❗ Most recently, and most thoroughly, tested on 5.3. Versions 5.1 and 5.2
    _should_ be compatible, but have not been completely validated with the most
    recent changes to the testing toolkit.
* ❗ Most recently, tested on 6.2. Other Versions of 6.x
    _should_ be compatible, but have not been completely validated with the most
    recent changes to the testing toolkit.
  * ❕ The script automation assumes that the API is running in IIS, not Docker.
    If running with Docker or from Visual Studio, the tests will complete, but
    there may be an error at the end about inability to stop the World Wide Web
    Publishing Service. This can be ignored.
* [Python](https://www.python.org/) 3.9+ (tested with 3.9.4)
* [Poetry](https://python-poetry.org/)
* PowerShell 5.0+ to use the full toolkit, including metric collection from
  Windows, IIS, and SQL Server.
  * You may need to change your PowerShell security to allow running downloaded
    scripts, for example with this command: `Set-ExecutionPolicy bypass -Scope
    CurrentUser -Force`.
  * Install the latest [SqlServer
    module](https://www.powershellgallery.com/packages/Sqlserver) on the
    test host and the database server
  * Install the [Credential Manager
    module](https://www.powershellgallery.com/packages/CredentialManager/2.0)
    module on the test host.
  * You might also need to configure TLS 1.2.
  * Tested in: PowerShell 5.1 and PowerShell 7.2.
* The user running the tests must be able to connect to the Web Server and the
  Database Server with Windows authentication, with sys admin permissions in SQL
  Server. You will be prompted to enter your credentials. _This only applies
  when using `run-tests.ps1`, which needs the user account for collecting
  metrics and (optionally) performing a database restore_.

## Getting Started

* Clone [this
  repository](https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing)
  using Git or download a Zip file for the [2.0 Paging Volume
  Tests](https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing/releases)
  release.
* Create a `.env` file in the root directory, based on `.env.example`. Customize
  for your installation and testing requirements.
  * When `PERF_DB_RESTORE: True` is used, the toolkit will try to restore the
    database to a known good state using the specified backup file. The backup
    file path in the `.env` file must be on the SQL Server.

## Paging Tests

### Paging Configuration

In the `.env` file:

* To test _all_ resources, comment out the `PERF_RESOURCE_LIST` entry.
* For more information on the settings, see the [edfi-paging-test
    README](../src/edfi-paging-test/README.md)

## Running the Paging Volume Tests

From the root folder, simply call the `run-tests.ps1` file while running **in
Administrator mode**.

```bash
./run-tests.ps1 -Type paging
```

Server metrics will be output to the `./TestResults/runner` directory. Paging
test results will be in a dated sub-directory, e.g.
`./TestResults/YYYY-mm-dd-HH-MM-SS`.

## SIS Certification Performance Tests

These tests cover the resources that are used in the Ed-Fi SIS Certification
program, and thus represent a broad swath of the most frequently used resources
in the Ed-Fi community. There are three operational modes described below, with
different run times and purposes.

### SIS Certification Configuration

The following settings are specific to the SIS Certification performance tests;
please see [edfi-performance-test](../src/edfi-performance-test/) for more information.

```none
PERF_TEST_TYPE=change_query
PERF_DELETE_RESOURCES=true
PERF_FAIL_DELIBERATELY=false
CLIENT_COUNT=100
SPAWN_RATE=25
RUN_TIME_IN_MINUTES=30
PERF_API_PREFIX="/data/v3/ed-fi"
PERF_API_OAUTH_ENDPOINT="/oauth/token"
```

Valid `PERF_TEST_TYPE` values are:

* `VOLUME`
* `PIPECLEAN`
* `CHANGE_QUERY`

### Running the SIS Certification Performance Tests

The PowerShell scripts provide several configuration modes with some default
settings that will override anything you have in the `.env` file.

Output files will be placed into a date-and-time stamped sub-directory of the
configured output directory.

#### Pipeclean

Runs one client for about one minute, performing a simple set of CRUD operations
on the available resources.

```bash
./run-tests.ps1 -Type pipeclean
```

#### Volume

Runs more complex data manipulations (create, update, and delete, with
relatively few read calls) on the available resources. Runs for 30 minutes with
100 clients in parallel.

```bash
./run-tests.ps1 -Type volume
```

#### Stress

Executes the volume test suite, but ramping up the client count (and thus the
number of requests) by 10-fold.

```bash
./run-tests.ps1 -Type stress
```

#### Soak

Executes the volume test suite, but ramping up the client count to 500 and
running for 48 hours.

```bash
./run-tests.ps1 -Type soak
```

#### Change Queries

Executes GET requests using Change Queries on all resources, running for
whatever length of time is specified in the config file, with only a single
client.

```bash
./run-tests.ps1 -Type changequeries
```

## Troubleshooting

* Double-check settings in the `.env` file.
* Make sure the API is running and can be accessed from the machine running
  these tests.
* Make sure that the database is running, can be accessed from the machine
  running these tests, and supports integrated security.
* Confirm that the database backup conforms to the features and extensions in
  the ODS/API code. For example, if the backup file was created from a database
  that did not include change queries, then make sure the change queries feature
  is disabled in the API project's `appsettings.json` file. Similarly, check
  that any extensions used by the API are actually installed in the database
  backup.
