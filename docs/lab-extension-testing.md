# Lab Exercise - Testing Extensions

This lab exercise, walks through the process of adding test cases for extensions to the API.

## Goal

The EPDM (formerly Teacher Preparation Data Model) extension enables comprehensive data
aggregation over the span of a educator's entire career, from application to and enrollment
into an EPP, through knowledge and skills demonstrated in fieldwork experiences,
to placement and performance as an in-service educator.
This extension includes candidate endpoints shown below.
The goal of this exercise is to create tests for this endpoint, incorporating them into both
the pipeclean and volume test playbooks.

![Screenshot of SwaggerUI showing GET, POST, PUT, and DELETE for /tpdm/candidates](images/candidates-resource.jpg)

For reference, here is a sample resource body that can be POSTed in SwaggerUI to create a new Candidate.

```javascript
{
    "id": "f251e34691f145eebddaa4af80a83a9a",
    "candidateIdentifier": "1000042",
    "birthDate": "2005-10-03",
    "economicDisadvantaged": false,
    "firstGenerationStudent": false,
    "firstName": "Bryce",
    "hispanicLatinoEthnicity": false,
    "lastSurname": "Beatty",
    "personalTitlePrefix": "M",
    "sexDescriptor": "uri://ed-fi.org/SexDescriptor#Not Selected",
    "addresses": [
      {
        "addressTypeDescriptor": "uri://ed-fi.org/AddressTypeDescriptor#Physical",
        "city": "Madison",
        "postalCode": "37598",
        "stateAbbreviationDescriptor": "uri://ed-fi.org/StateAbbreviationDescriptor#AA",
        "streetNumberName": "124 North Old Drive",
        "apartmentRoomSuiteNumber": "922",
        "buildingSiteNumber": "53",
        "doNotPublishIndicator": false,
        "periods": []
      }
    ],
    "disabilities": [],
    "electronicMails": [],
    "languages": [],
    "otherNames": [],
    "personalIdentificationDocuments": [],
    "races": [
      {
        "raceDescriptor": "uri://ed-fi.org/RaceDescriptor#Black - African American"
      }
    ],
    "telephones": []
  }
```

## Pre-Requisites

1. ODS and API version 5.3 or higher (includes TPDM extension out of the box) running on a
   server with sandbox deployment.
1. The performance test environment setup according to [User Guide](user-guide.md).
1. (optional) Familiarize yourself with [How to Create Resource
   Tests](how-to-create-tests.md). This exercise will walk you through steps
   that are described in more detail in that document.

## Create the Factory Class

The Factory class contains the data that will be posted to create a new
resource. These data are equivalent to the JSON payload shown in the example
above. We'll take advantage of the utility functions provided by this framework:

* `RandomSuffixAttribute` for a random `applicationIdentifier`
* `RandomDateAttribute` to set the `birthDate`
* `build_descriptor` to create the descriptor values.

Create file `candidate.py` in `~Suite-3-Performance-Testing\src\edfi-performance-test\edfi_performance_test\factories\resources`
with the following contents:

```python
import factory
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import (
    RandomDateAttribute,
    RandomSuffixAttribute,
)


class CandidateFactory(APIFactory):
    candidateIdentifier = RandomSuffixAttribute("Candidate")
    addresses = factory.List(
        [
            factory.Dict(
                dict(
                    addressTypeDescriptor=build_descriptor("AddressType", "Physical"),
                    stateAbbreviationDescriptor=build_descriptor(
                        "StateAbbreviation", "NY"
                    ),
                    city="New York",
                    postalCode="10128",
                    streetNumberName="1234 Sesame St.",
                )
            )
        ]
    )
    birthDate = RandomDateAttribute()
    firstName = "Gordon"
    lastSurname = "Robinson"
    hispanicLatinoEthnicity = False
    sexDescriptor = build_descriptor("Sex", "Male")
```

## Create the Client Class

The parent class for API clients, `EdFiAPIClient`, defines this constant:

```python
API_PREFIX = '/data/v3/ed-fi'
```

However, the extensions are not at this path. Instead of `ed-fi` we need
`tpdm`. Thus in the code below, we need to initialize api_prefix value. This is
only appropriate for extensions and not for new additions to the core Ed-Fi API.

Create file `candidate.py` in `~Suite-3-Performance-Testing\src\edfi-performance-test\edfi_performance_test\api\client`
with the following contents:

```python
from locust.clients import HttpSession
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class CandidateClient(EdFiAPIClient):
    endpoint = 'candidates'

    def __init__(self, client: HttpSession, token: str = "", api_prefix: str = ""):
        super(CandidateClient, self).__init__(client, token, '/data/v3/tpdm')
```

## Create the Pipeclean Test

In the pipeclean testing, we need to setup a value to change in the PUT request. Let's change the `hispanicLatinoEthnicity` from false to true.
Create file `candidate.py` in `~Suite-3-Performance-Testing\src\edfi-performance-test\edfi_performance_test\tasks\pipeclean`
with the following contents:

```python
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import EdFiPipecleanTestBase


class CandidatePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'hispanicLatinoEthnicity'
    update_attribute_value = True
```

## Create the Volume Test

Create file `candidate.py` in `~Suite-3-Performance-Testing\src\edfi-performance-test\edfi_performance_test\tasks\volume` with the following contents:

```python
from locust import task

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class CandidateVolumeTest(EdFiVolumeTestBase):
    @task
    def run_sesame_street_scenarios(self):
        self.run_scenario('hispanicLatinoEthnicity', True)
```

## Execute Tests

The following commands will run both tests _only_, without executing any of the
other pipeclean or volume test scenarios. However, if you run the full test
suite, it will include the new `Candidate` tests (see [User Guide](user-guide.md) for details).
Open a PowerShell prompt. The second command assumes that you cloned the code repository into
`c:\src\Suite-3-Performance-Testing`; adjust as needed. The pipeclean test will naturally
finish running more quickly than the volume tests. In this example we [limit the
volume
tests](https://docs.locust.io/en/stable/running-without-web-ui.html#setting-a-time-limit-for-the-test)
to run only for 3 minutes.

```powershell
cd c:\src\Suite-3-Performance-Testing\src\edfi-performance-test
poetry run python edfi_performance_test --baseUrl "http://localhost:54746" --key  "emptyKey" --secret "emptysecret"  --testType "pipeclean" --testList  "CandidatePipecleanTest"
poetry run python edfi_performance_test --baseUrl "http://localhost:54746" --key  "emptyKey" --secret "emptysecret"  --testType "volume" --testList  "CandidateVolumeTest" --runTimeInMinutes "3"
```

The test runs [output test results](https://docs.locust.io/en/stable/retrieving-stats.html) to CSV files.
The output directory can be configured with `--output` parameter.

## Analyze Test Results

Your results will differ from those shown below based on factors include
hardware characteristics, what else is running on the server, and the size of
the database that you run against (if running on something other than the
sandbox). The response times are in milliseconds (ms).

### Pipeclean Requests

Some highlights:

* No failures occurred.
* Not surprisingly, creating a new resource took longer than other requests.
* Because Locust runs test clients in parallel, the total requests per second is
  not the average of the individual values. In this case we managed
  approximately 42 requests per second.

(!) These data are from a small-ish VM installed in single-server mode, which is far
from ideal. In other words, these numbers are not reflective of what a good
production setup can achieve.

| Type     | Name                                                                       | # reqs |    # fails  |    Avg |     Min |    Max  | Med  |   req/s | failures/s|
| -------- | ---------------------------------------------------------------------------|------- |------------ |------- | ------- | ------- |------|---------|-----------|
| GET      | /data/v3/tpdm/candidates                                                   |     1  |   0(0.00%)  |    676 |    676  |   676   |  676 |    0.00 |    0.00   |
| POST     | /data/v3/tpdm/candidates                                                   |     1  |   0(0.00%)  |     68 |     68  |    68   |   68 |    0.00 |    0.00   |
| DELETE   | /data/v3/tpdm/candidates/{id}                                              |     1  |   0(0.00%)  |     35 |     35  |    35   |   35 |    0.00 |    0.00   |
| GET      | /data/v3/tpdm/candidates/{id}                                              |     1  |   0(0.00%)  |     44 |     44  |    44   |   44 |    0.00 |    0.00   |
| PUT      | /data/v3/tpdm/candidates/{id}                                              |     1  |   0(0.00%)  |     52 |     52  |    52   |   52 |    0.00 |    0.00   |
| POST     | /oauth/token                                                               |     1  |   0(0.00%)  |    117 |    117  |   117   |  117 |    0.00 |    0.00   |
|Aggregated|                                                                            |     6  |   0(0.00%)  |    165 |     35  |   676   |   53 |    0.00 |    0.00   |


### Volume Requests

As expected from "volume tests", there are significantly more requests this
time. Thankfully there are still no failures. Interestingly, the median response
time of the volume tests is consistent with the time on the pipeclean test,
which suggests that the performance is fairly stable / consistent from one
request to the next.

| Type     |Name                                                                        |# reqs  | # fails     |  Avg   |  Min    | Max   | Med  | req/s   |Failures/s |
| -------- | ---------------------------------------------------------------------------|------- |------------ |--------| ------- | ----- |------|---------|-----------|
| POST     | /data/v3/tpdm/candidates                                                   | 482    |  0(0.00%)   | 1325   |287      | 5566  | 910  | 2.7     |    0.00   |
| DELETE   | /data/v3/tpdm/candidates/{id}                                              | 474    |  0(0.00%)   | 1076   |245      | 5528  | 730  | 2.6     |    0.00   |
| PUT      | /data/v3/tpdm/candidates/{id}                                              | 241    |  0(0.00%)   | 1378   |360      | 14721 | 910  | 1.3     |    0.00   |
| POST     | /oauth/token                                                               | 280    |  0(0.00%)   | 932    |59       | 7776  | 650  | 1.5     |    0.00   |
|Aggregated|                                                                            | 1477   |  0(0.00%)   | 1179   |59       | 14721 | 820  | 8.2     |    0.00   |

### Volume Distribution

The 50% column represents the median and is the same value that you see in the
"Median response time" column above. This table gives us some sense of
consistency and can be used if you have an objective of achieving a certain
throughput for, let's say, 95% of requests.


| Type     |Name                                                                        | 50%    | 66%   | 75%   | 80%   | 90%   |  95% |98%   |99%   |99.90%|99.99%|100% |
| -------- | ---------------------------------------------------------------------------|------- |------ |-------| ----- | ----- |------|------|----- |----- |----- |-----|
| POST     | /data/v3/tpdm/candidates                                                   | 910    | 1200  | 1600  | 2000  | 2700  | 3500 | 4300 | 4400 | 5600 | 5600 |5600 |
| DELETE   | /data/v3/tpdm/candidates/{id}                                              | 730    | 1000  | 1400  | 1600  | 2000  | 2700 |3700  | 4300 | 5500 | 5500 |5500 |
| PUT      | /data/v3/tpdm/candidates/{id}                                              | 910    | 1200  | 1600  | 1800  | 2400  | 3600 |4500  | 6400 | 15000| 15000|15000|
| POST     | /oauth/token                                                               | 650    | 800   | 1200  | 1400  | 1700  | 2100 |2600  | 4600 | 7800 | 7800 |7800 |
|Aggregated|                                                                            | 820    | 1100  | 1400  | 1600  | 2200  | 3000 |4100  | 4500 | 7800 | 15000|15000|

## Further Experimentation

### Larger Initial Data Set

How well does this endpoint respond as the amount of data _already in the table_
increases? Artificially add 10,000 rows to the `Candidate` table with the
following script, and then re-run the volume tests using the same command from
earlier:

```sql
DECLARE @ApplicantIdentifier as NVARCHAR(100)
DECLARE @Counter as INT = 0
DECLARE @Sex as INT = 0

WHILE @Counter < 10000
BEGIN
    SELECT @ApplicantIdentifier = CONCAT(N'padding-the-database-', @Counter)

    -- Evenly distribute the applicants by sex
    SELECT @Sex = CASE WHEN @Counter % 3 = 0 THEN 8539 WHEN @Counter % 3 = 1 THEN 8540 ELSE 8541 END

    exec sp_executesql N'INSERT INTO gb.Applicant (LastModifiedDate, CreateDate, Id, BirthDate, CitizenshipStatusDescriptorId, FirstName, GenerationCodeSuffix, HighestCompletedLevelOfEducationDescriptorId, HighlyQualifiedAcademicSubjectDescriptorId, HighlyQualifiedTeacher, HispanicLatinoEthnicity, LastSurname, LoginId, MaidenName, MiddleName, PersonalTitlePrefix, SexDescriptorId, YearsOfPriorProfessionalExperience, YearsOfPriorTeachingExperience, ApplicantIdentifier, EducationOrganizationId) VALUES (@p0, @p1, @p2, @p3, @p4, @p5, @p6, @p7, @p8, @p9, @p10, @p11, @p12, @p13, @p14, @p15, @p16, @p17, @p18, @p19, @p20)',N'@p0 datetime,@p1 datetime,@p2 uniqueidentifier,@p3 datetime,@p4 int,@p5 nvarchar(4000),@p6 nvarchar(4000),@p7 int,@p8 int,@p9 bit,@p10 bit,@p11 nvarchar(4000),@p12 nvarchar(4000),@p13 nvarchar(4000),@p14 nvarchar(4000),@p15 nvarchar(4000),@p16 int,@p17 decimal(28,5),@p18 decimal(28,5),@p19 nvarchar(4000),@p20 int',
    @p0='2018-10-05 11:50:27.570',@p1='2018-10-05 11:50:27',@p2='A683BF41-F625-4640-AAC8-C6338A03045A',@p3='8233-03-24 00:00:00',@p4=NULL,@p5=ApplicantIdentifier,@p6=NULL,@p7=NULL,@p8=NULL,@p9=NULL,@p10=NULL,@p11=ApplicantIdentifier,@p12=NULL,@p13=NULL,@p14=NULL,@p15=NULL,@p16=@Sex,@p17=3.00000,@p18=2.00000,@p19=@ApplicantIdentifier,@p20=255901001

    SET @Counter = @Counter + 1
END
```

#### Larger Data Set Results

| Method | Name | # requests | # failures | Median response time | Average response time | Min response time | Max response time | Average Content Size | Requests/s |
| ------ | ---- | ---------- | ---------- | -------------------- | --------------------- | ----------------- | ----------------- | -------------------- | ---------- |
| POST | /data/v3/grand-bend/applicants | 625 | 0 | 0 | 27 | 0 | 976 | 0 | 3.51 |
| DELETE | /data/v3/grand-bend/applicants/{id} | 625 | 0 | 30 | 31 | 14 | 197 | 0 | 3.51 |
| PUT | /data/v3/grand-bend/applicants/{id} | 625 | 0 | 15 | 15 | 0 | 321 | 0 | 3.51 |
| POST | /oauth/token | 20 | 0 | 5300 | 6308 | 16 | 15453 | 108 | 0.11 |
| None | Total | 1895 | 0 | 16 | 90 | 0 | 15453 | 1 | 10.63 |

#### Larger Data Set Distribution

| Name | # requests | 50% | 66% | 75% | 80% | 90% | 95% | 98% | 99% | 100% |
| ---- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
| POST /data/v3/grand-bend/applicants | 625 | 0 | 15 | 16 | 16 | 16 | 16 | 670 | 910 | 980 |
| DELETE /data/v3/grand-bend/applicants/{id} | 625 | 30 | 31 | 31 | 32 | 32 | 34 | 130 | 160 | 200 |
| PUT /data/v3/grand-bend/applicants/{id} | 625 | 15 | 16 | 16 | 16 | 16 | 31 | 46 | 270 | 320 |
| POST /oauth/token | 20 | 6400 | 9400 | 11000 | 12000 | 14000 | 15000 | 15000 | 15000 | 15000 |
| Total | 1895 | 16 | 16 | 30 | 30 | 31 | 32 | 270 | 930 | 15000 |

#### Larger Data Set Analysis

* No failures occurred.
* POST and PUT performance is fairly is consistent with the original volume
  testing for 90% of the calls, but the remainder are starting to take longer.
* DELETE times are nearly double what they were before.
* The outliers were much higher, especially for the POST request.
* Token response time is terrible! That is very odd and would not seem to have
  anything to do with the `Candidate` resource.

### Additional Indexing

Presumably someone wants to query this Applicants table and have a very fast response. The primary key is the pairing (`EducationOrganizationId`, `ApplicantIdentifier`). Perhaps someone is interested in viewing applicant demographics using the following query:

```sql
SELECT
    [SexDescriptor].[CodeValue] as [Sex],
    [CitizenshipDescriptor].[CodeValue] as [Citizenship],
    [HispanicLatinoEthnicity],
    COUNT(1)
FROM
    [gb].[Applicant]
LEFT OUTER JOIN
    [edfi].[Descriptor] as [SexDescriptor] ON
        [Applicant].[SexDescriptorId] = [SexDescriptor].[DescriptorId]
LEFT OUTER JOIN
    [edfi].[Descriptor] as [CitizenshipDescriptor] ON
        [Applicant].[CitizenshipStatusDescriptorId] = [CitizenshipDescriptor].[DescriptorId]
GROUP BY
    [SexDescriptor].[CodeValue],
    [CitizenshipDescriptor].[CodeValue],
    [HispanicLatinoEthnicity]
```

Although it is very contrived, create an index to optimize this query:

```sql
CREATE INDEX [IX_Applicant_Demographics] ON [gb].[Applicant] (
    [SexDescriptorId],
    [CitizenshipStatusDescriptorId]
) INCLUDE (
    [HispanicLatinoEthnicity]
)
```

Re-run the performance tests to see what the impact of this index is.

#### Indexing Results

| Method | Name | # requests | # failures | Median response time | Average response time | Min response time | Max response time | Average Content Size | Requests/s |
| ------ | ---- | ---------- | ---------- | -------------------- | --------------------- | ----------------- | ----------------- | -------------------- | ---------- |
| POST | /data/v3/grand-bend/applicants | 609 | 0 | 0 | 28 | 0 | 1049 | 0 | 3.41 |
| DELETE | /data/v3/grand-bend/applicants/{id} | 609 | 0 | 30 | 30 | 9 | 203 | 0 | 3.41 |
| PUT | /data/v3/grand-bend/applicants/{id} | 609 | 0 | 15 | 17 | 0 | 421 | 0 | 3.41 |
| POST | /oauth/token | 20 | 0 | 5700 | 6627 | 14 | 15751 | 108 | 0.11 |
| None | Total | 1847 | 0 | 16 | 96 | 0 | 15751 | 1 | 10.34 |

#### Indexing Distribution

| Name | # requests | 50% | 66% | 75% | 80% | 90% | 95% | 98% | 99% | 100% |
| ---- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- | ---- |
| POST /data/v3/grand-bend/applicants | 609 | 0 | 15 | 16 | 16 | 16 | 16 | 640 | 670 | 1000 |
| DELETE /data/v3/grand-bend/applicants/{id} | 609 | 30 | 31 | 31 | 31 | 32 | 32 | 110 | 160 | 200 |
| PUT /data/v3/grand-bend/applicants/{id} | 609 | 15 | 16 | 16 | 16 | 16 | 31 | 47 | 390 | 420 |
| POST /oauth/token | 20 | 6700 | 9800 | 12000 | 13000 | 15000 | 16000 | 16000 | 16000 | 16000 |
| Total | 1847 | 16 | 16 | 30 | 30 | 31 | 32 | 390 | 1000 | 16000 |

#### Indexing Analysis

* Average response times, and the 95% threshold, are basically unchanged.
* Those token calls are taking longer and longer.

Conclusion: adding this index, at this volume of data, does not have a clear
negative impact, and is therefore the risk of introducing a performance problem
in production is very low.
