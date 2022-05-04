# Suite-3-Performance-Testing

Performance testing framework for the Ed-Fi ODS technical suite 3

## Version 2.0

May, 2022

The [current release](docs/release-notes.md) temporarily removes support for the
older performance tests, while adding support for Paging Volume Tests. These
tests execute GET requests across all selected resources, paging through all
available data. This functionality therefore supports running before/after
comparison testing on GET requests, which can help identify missing indexes,
assess performance changes in the .NET code, or validate the effects of
infrastructure changes (such as adding webserver load balancing or upsizing a
virtual machine).

There are two ways to run these Paging Volume Tests:

* Directly run the [edfi-paging-test](src/edfi-paging-test) package against any
  ODS/API 5.1 or newer, running in any environment and with any database.
  * See the [README](src/edfi-paging-test/README.md) for details on how to run
    this tool.
* Or, run `run-tests.ps1` to capture additional Windows Server metrics and
  logging when running the ODS/API in IIS on Windows with SQL Server on the
  backend.
  * See the [User Guide](docs/user-guide.md) for a full description of
    requirements and run instructions.

Upcoming releases will re-introduce support for write-based tests, and _might_
add support for executing the Paging Volume Tests on ODS/API 5.0 and older.

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
