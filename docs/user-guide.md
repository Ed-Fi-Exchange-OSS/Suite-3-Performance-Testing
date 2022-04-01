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

See [Paging Volume Test Getting Started](/src/edfi-paging-test/README.md#Getting%20Started) for setup details.

## Usage

### Running a locust test with performance metrics and logs (Recommended)

1. Start the local Ed-Fi ODS API.  (See
   [here](https://techdocs.ed-fi.org/display/ODSAPIS3V53/Getting+Started+-+Source+Code+Installation)
   for installation and invocation instructions.)
1. Open a command prompt window and cd to the root to the repository. (`cd
   C:\dev\Suite-3-Performance-Testing`)
1. Run the following command to run the standard volume test: `run-tests pagevolume`
1. Volume, pipeclean, soak, stress and change query test are not available at this time
1. Once the test finishes, you can look inside the TestResults directory, which
   will be located at the root of the repository to see log entries, performance
   metrics, and test results.
