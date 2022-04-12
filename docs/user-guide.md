# User Guide for the Suite 3 Performance Test Kit

## Scope

This document covers:

* Paging Volume Tests

Not included:

* "SIS Certification" pipeclean, volume, load, change query, and soak tests.
  These are temporarily deprecated due to out-of-date libraries and Python
  version.

## Pre-requisites

* [Python](https://www.python.org/) 3.9+ (tested with 3.9.4)
* [Poetry](https://python-poetry.org/)
* PowerShell 5.0+ to use the full toolkit, including metric collection from
  Windows, IIS, and SQL Server.
  * Be sure to install the latest [SqlServer
    module](https://www.powershellgallery.com/packages/Sqlserver)
* The user running the tests must be able to connect to the Web Server and the
  Database Server with Windows authentication, with sys admin permissions in SQL
  Server. _This only applies when using `run-tests.ps1`, which needs the user
  account for collecting metrics and (optionally) performing a database
  restore_.

## Getting Started

* Clone [this
  repository](https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing)
  using Git or download a Zip file for the [2.0 Paging Volume
  Tests](https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing/releases)
  release.
* Install all application dependencies:

  ```bash
  cd src/edfi-paging-test
  poetry install
  ```

* Create a `.env` file in `src/edfi-paging-test` (can start with
  `.env.example`). Customize for your installation and testing requirements.
  * To test _all_ resources, comment out the `PERF_RESOURCE_LIST` entry.
  * For more information on the settings, see the [edfi-paging-test
    README](../src/edfi-paging-test/README.md)
* Customize the `test-config.json` file using the same information input to the
  `.env` file (in the future these will be merged).
  * When `"restore_database": true` is used, the toolkit will try to restore the
    database to a known good state using the specified backup file. The two SQL
    file paths in the file must be on the SQL Server. If SQL Server is running
    on another machine, then use UNC paths or drive mappings to access the
    proper paths.

## Running the Paging Volume Tests

From the root folder, simply call the `run-tests.ps1` file.

```bash
./run-tests.ps1
```

Server metrics will be output to the `./TestResults` directory. Paging test
results will found in whatever directory was specified in the `.env` file.

## Troubleshooting

* Double-check settings in the `.env` and `test-config.json` files
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
