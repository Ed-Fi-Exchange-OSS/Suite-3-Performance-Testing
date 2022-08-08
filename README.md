# Suite-3-Performance-Testing

Performance testing framework for the Ed-Fi ODS technical suite 3, including the
following test paths:

1. [Paging Performance](src/edfi-paging-test), for timing retrieval of _all_
   data in the API, or on selected resources.
2. [SIS Certification Testing](src/edfi-performance-test/) covering all
   endpoints used in the SIS certification process with these scenarios:
   1. **Pipeclean**: simple POST, GET, PUT, and DELETE operations that prove the API
      is fully operational.
   2. **Volume**: runs a large volume of POST, PUT, and DELETE operations with
      parallel clients and randomized workload.
   3. **Change Queries**: executes the change queries process.

See the [User Guide](docs/user-guide.md) for a full description of requirements
and run instructions.

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
