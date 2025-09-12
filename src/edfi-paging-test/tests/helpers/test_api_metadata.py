# # SPDX-License-Identifier: Apache-2.0
# # Licensed to the Ed-Fi Alliance under one or more agreements.
# # The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# # See the LICENSE and NOTICES files in the project root for more information.


from typing import Dict, List
import pytest
from pathlib import Path
import pook
from edfi_paging_test.helpers.api_metadata import (
    get_filters_by_resource_name,
    normalize_resource_path,
)

MOCK_BASE_URL: str = "https://example.com/v5.3/api"

fake_base_api_metadata_json: str = Path(
    "tests/helpers/api_metadata/base_api_metadata.json"
).read_text()
fake_openapi_metadata_json: str = Path(
    "tests/helpers/api_metadata/openapi_metadata.json"
).read_text()
fake_resource_metadata_json: str = Path(
    "tests/helpers/api_metadata/resource_metadata.json"
).read_text()


def describe_when_requesting_resource_paths():
    @pytest.fixture
    def resource_paths() -> Dict[str, List[str]]:
        # arrange
        pook.activate()
        pook.get(
            MOCK_BASE_URL,
            response_json=fake_base_api_metadata_json,
            reply=200,
        )
        pook.get(
            f"{MOCK_BASE_URL}/metadata/",
            response_json=fake_openapi_metadata_json,
            reply=200,
        )
        pook.get(
            f"{MOCK_BASE_URL}/metadata/data/v3/resources/swagger.json",
            response_json=fake_resource_metadata_json,
            reply=200,
        )

        # act
        return get_filters_by_resource_name(MOCK_BASE_URL, True)

    def it_should_have_correct_length(resource_paths):
        assert len(resource_paths) == 129

    def it_should_have_a_correct_sampling_of_resources(resource_paths):
        assert resource_paths['academicWeeks'] == ['weekIdentifier',
                                                   'schoolId', 'beginDate', 'endDate', 'totalInstructionalDays']
        assert resource_paths['tpdm/candidates'] == [
            'candidateIdentifier',
            'personId',
            'sourceSystemDescriptor',
            'birthCountryDescriptor',
            'englishLanguageExamDescriptor',
            'genderDescriptor',
            'limitedEnglishProficiencyDescriptor',
            'sexDescriptor',
            'birthSexDescriptor',
            'birthStateAbbreviationDescriptor',
            'birthCity',
            'birthDate',
            'birthInternationalProvince',
            'dateEnteredUS',
            'displacementStatus',
            'economicDisadvantaged',
            'firstGenerationStudent',
            'firstName',
            'generationCodeSuffix',
            'hispanicLatinoEthnicity',
            'lastSurname',
            'maidenName',
            'middleName',
            'multipleBirthStatus',
            'personalTitlePrefix',
        ]
        assert resource_paths['learningStandards'] == [
            'learningStandardId',
            'parentLearningStandardId',
            'learningStandardCategoryDescriptor',
            'learningStandardScopeDescriptor',
            'courseTitle',
            'description',
            'learningStandardItemCode',
            'namespace',
            'successCriteria',
            'uri',
        ]
        assert resource_paths['surveySectionResponseStaffTargetAssociations'] == [
            'staffUniqueId',
            'namespace',
            'surveyIdentifier',
            'surveyResponseIdentifier',
            'surveySectionTitle',
        ]


def describe_when_normalizing_paths():
    def it_should_remove_edfi_prefix():
        assert normalize_resource_path("/ed-fi/student") == "student"

    def it_should_remove_edfi_prefix_and_preserve_case():
        assert normalize_resource_path("/ed-fi/studentSchoolAssociation") == "studentSchoolAssociation"

    def it_should_remove_leading_slash():
        assert normalize_resource_path("/tpdm/candidates") == "tpdm/candidates"
