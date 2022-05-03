# User Guide for the Suite 3 Performance Test Kit

## Scope

This document covers execution of the following tests in a Windows / SQL Server
environment:

* Paging Volume Tests

Not included:

* "SIS Certification" pipeclean, volume, load, change query, and soak tests.
  These are temporarily deprecated due to out-of-date libraries and Python
  version.

## Pre-requisites

The Python, Poetry, and Powershell requirements below can be installed
with the help of the scripts in the [eng directory](../eng).

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
  * To test _all_ resources, comment out the `PERF_RESOURCE_LIST` entry.
  * For more information on the settings, see the [edfi-paging-test
    README](../src/edfi-paging-test/README.md)
  * When `PERF_DB_RESTORE: True` is used, the toolkit will try to restore the
    database to a known good state using the specified backup file. The backup
    file path in the `.env` file must be on the SQL Server.

## Running the Paging Volume Tests

From the root folder, simply call the `run-tests.ps1` file while running **in
Administrator mode**.

```bash
./run-tests.ps1
```

Server metrics will be output to the `./TestResults/runner` directory. Paging
test results will be in a dated sub-directory, e.g.
`./TestResults/YYYY-mm-dd-HH-MM-SS`.

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
