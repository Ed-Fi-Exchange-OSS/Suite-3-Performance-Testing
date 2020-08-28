# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client.composite import EdFiCompositeClient


class EnrollmentCompositeClient(EdFiCompositeClient):
    API_PREFIX = '/composites/v3/ed-fi/enrollment'
    constants = {
        'schools': None,
        'sections': None,
        'localEducationAgencies': None,
        'staffs': None,
        'students': None
    }


class LocalEducationAgencyEnrollmentCompositeClient(EnrollmentCompositeClient):
    endpoint = 'localEducationAgencies'


class SchoolEnrollmentCompositeClient(EnrollmentCompositeClient):
    endpoint = 'schools'


class SectionEnrollmentCompositeClient(EnrollmentCompositeClient):
    endpoint = 'sections'


class StaffEnrollmentCompositeClient(EnrollmentCompositeClient):
    endpoint = 'staffs'


class StudentEnrollmentCompositeClient(EnrollmentCompositeClient):
    endpoint = 'students'
