# Release Notes

## Performance Testing 2.0 Release Notes

April, 2022

* Supports volume testing of _paging_ get requests
* Temporarily deprecates the 1.x SIS Certification-related volume, load, and soak tests
  * Contains outdated and insecure libraries
  * Will be restored with 2.1 release
  * Please see [Release
    1.2.0](https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing/tree/1.2.0)
    for the last working version of the original test suite.

For more information on the Paging Volume Tests, see:

* [User Guide](user-guide.md) - full install and execution instructions (high
  level)
* [src/edfi-paging-test](../src/edfi-paging-test/) - instructions for direct
  execution of the test kit (low level)

## Performance Testing 1.2.0 Release Notes

* Support for Change Queries testing using `change_query_tests.py`.
* Updates to the Assessment API due to changes in the data standard.
* Pipeclean testing for composites.
* Refactoring of API client dependency handling, described in [How To Create
  Tests](how-to-create-tests.md#complex-clients-1-dependencies).
* Query for database logical name when restoring from backup, instead of
  hard-coding to the populated template name.
* Dates now need to be in format `YYYY-mm-dd` and should be formatted using the
  shared function `formatted_date`.
