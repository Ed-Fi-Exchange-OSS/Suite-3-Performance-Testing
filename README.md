# Suite-3-Performance-Testing

Performance testing framework for the Ed-Fi ODS technical suite 3

## Version 2.0

April, 2022

* Supports volume testing of _paging_ get requests
* The script process using `run-tests.ps1` supports SQL Server only. The Python
  tool [src/edfi-paging-test](../src/edfi-paging-test/README.md) does not
  connect to the database, and therefore can run without the PowerShell script
  for PostgreSQL installations.
* Temporarily deprecates the 1.x SIS Certification-related volume, load, and soak tests
  * Contains outdated and insecure libraries
  * Will be restored with 2.1 release
  * Please see [Release
    1.2.0](https://github.com/Ed-Fi-Exchange-OSS/Suite-3-Performance-Testing/tree/1.2.0)
    for the last working version of the original test suite.

For more information on the Paging Volume Tests, see:

* [User Guide](docs/user-guide.md) - full install and execution instructions (high
  level)
* [src/edfi-paging-test](src/edfi-paging-test/README.md) - instructions for direct
  execution of the test kit (low level)

## Support

These scripts are provided as-is, and the Alliance welcomes feedback on
additions or changes that would make these resources more user friendly.
Feedback is best shared by raising a ticket on [Ed-Fi
Tracker](https://tracker.ed-fi.org/) using component `performance-testing`.

## Legal Information

Copyright (c) 2022 Ed-Fi Alliance, LLC and contributors.

Licensed under the [Apache License, Version 2.0](LICENSE) (the "License").

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See [NOTICES](NOTICES.md) for additional copyright and license notifications.
