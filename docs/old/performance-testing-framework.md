# Performance Testing Framework

## Need/Problem Statement

The third version of the ODS / API was released in May 2018. Prior versions have
been tested and tuned for improved performance characteristics. Significant
changes have been made for this new release, necessitating additional testing.
While prior projects provided useful information for improving the API service,
their utility was limited in that they depended on custom-built applications and
configurations that were not easily re-usable.

The desired framework is intended for two audiences: the Ed-Fi Alliance and the
Ed-Fi community. Some elements of the deliverables will be specific to the
Alliance’s daily software development practices, but the core framework and
documentation will be broadly applicable. Thus, districts and partners will be
able to utilize the framework for running performance tests on their own system
configurations.  The following user stories reflect a generic “tester” persona
for either audience– most likely an IT professional executing various types of
testing.

1. Documentation: As a Tester, I want to receive clear documentation on the
   Ed-Fi performance testing framework, so that I can quickly configure and
   execute tests in my own environment.
1. Source Control: As a Tester, I want to retrieve all test framework components
   from a source control system, so that I can get the latest files at any time
   without having to transcribe information from a user interface.
1. Pipeclean Testing: As a Tester, I want to execute all API calls once with a
   single client (“user”), so that I know all test cases are functional and
   system components are running properly. OPTIONAL – see note below.
1. Volume Testing: As a Tester, I want to execute multi-threaded API calls,
   simulating multiple medium-to-large local education agencies connecting to a
   single ODS /API at the same time, so that I can establish performance
   characteristics and expectations for a state-wide system.
1. Stress Testing: As a Tester, I want to increase the data and API calls to the
   point where the ODS system becomes unresponsive, so that I can identify a
   “breaking point” in a standard server configuration.
1. Soak Testing: As a Tester, I want to execute volume testing continuously over
   several days, so that I can detect any gradual performance degradation.
1. Test Results: As a Tester, after each test session, I want to view a report
   describing the transactional performance of test cases and overall system
   characteristics (e.g. memory, cpu, etc), so that I can begin to identify
   bottlenecks and understand the performance characteristics of a particular
   system configuration.

## Functional Vision

### Vision and Goals

The completed project will provide the Ed-Fi Alliance with baseline performance
metrics for the ODS / API, analysis of bottlenecks, and recommendations for
server sizing for representative agency simulation sizes. The completed solution
will also provide tools and instructions for any Ed-Fi community member to
execute performance testing of an installation of the ODS and API and compare
results to baseline measurements. The solution framework will be listed in the
Ed-Fi Exchange for general community discovery.

### Requirements

1. Load seed data into the ODS through scripts
1. The ODS should be reset to a known-good starting point before each test
   session.
1. API tests cases are defined via text config files or scripts.
1. API test cases cover all resources in [Student Information Systems for ODS /
   API v3](https://techdocs.ed-fi.org/pages/viewpage.action?pageId=43582249k)
   and [Assessment Outcomes Management
   API](https://techdocs.ed-fi.org/display/EDFICERT/Assessment+Outcomes+Management+API+Certification).
   &dagger;
1. API test cases include calls that will generate errors.
1. General test cases will re-use an authentication token for a user with
   resource permissions covering all tested API resources.
1. Some test cases will use a more limited authentication scope that does not
   have access to the tested API resources.
1. Test cases are not compiled from Swagger metadata.
1. API execution is defined via text config files or scripts.
1. API execution utilizes off-the-shelf tools.
1. API execution utilizes free/open source tools.
1. Network resources and credentials are easily configured.
1. All framework artifacts will be stored in a git repository in the
   Ed-Fi-Alliance organization on GitHub.

&dagger; The certification specs cover insert, update, and delete, but not GET.
The volume testing will cover these and not GET. Pipeclean tests will cover GET
requests as well.

## Technical Implementation

### Platform

The [Locust](https://locust.io) testing platform has been selected for two main
reasons:

1. Code-driven tests
1. Minimal cost (implementation time and licensing)

Locust tests are written using Python and are easy to customize and extend. The
tests require basic programming skills to write and understand, but they end up
being readable, easily incorporated into source control, and can share complex
behavior. Even though it is free, Locust offers the following out of the box:

* Scalable load testing framework
* User-friendly UI
* Dev-friendly CLI
* Reporting
* Distributed computing

### Project Structure

* Root directory: execution scripts
  * Administration: automation scripts
  * docs: markdown documentation
  * edfi_performance: python source code
    * api
      * client: one file per API resource to test
    * config: global configuration class, no future modification expected
    * factories: one file per API resource to test
    * tasks
      * pipeclean: one file per API resource to test
      * volume: one file per API resource to test

See [How to Create Tests](how-to-create-tests.md) for more information on the
clients, factories, and tasks. In general, new tests will only add to these
directories without needing to change any existing files.