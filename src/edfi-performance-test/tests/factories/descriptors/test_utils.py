# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict, List
import pytest

from edfi_performance_test.factories.descriptors.utils import build_descriptor_dicts, build_descriptor


def describe_when_building_a_descriptor() -> None:
    @pytest.mark.parametrize("input, expected", [
        ("Title", "uri://ed-fi.org/TitleDescriptor#value"),
        ("title", "uri://ed-fi.org/TitleDescriptor#value"),
        ("titledescriptor", "uri://ed-fi.org/TitledescriptorDescriptor#value"),
        ("title_descriptor", "uri://ed-fi.org/TitleDescriptor#value"),
    ])
    def it_formats_the_descriptor_string_correctly(input: str, expected: str) -> None:
        actual = build_descriptor(input, "value")

        assert actual == expected


def describe_when_building_a_descriptor_dictionary() -> None:
    def describe_given_two_grade_levels() -> None:
        @pytest.fixture
        def result() -> List[str]:
            result = build_descriptor_dicts(
                "GradeLevel", ["Ninth grade", "Tenth grade"]
            )

            descriptors = [i['gradeLevelDescriptor'] for i in result]
            assert len(descriptors) == 2

            return descriptors

        @pytest.mark.parametrize("expected", [("uri://ed-fi.org/GradeLevelDescriptor#Ninth grade"), ("uri://ed-fi.org/GradeLevelDescriptor#Tenth grade")])
        def it_includes_all_grades(result, expected) -> None:
            assert expected in result

    def describe_given_a_telephone_number() -> None:
        @pytest.fixture
        def result() -> Dict[str, str]:
            result = build_descriptor_dicts(
               "InstitutionTelephoneNumberType", [("Main", {"telephoneNumber": "(950) 325-9465"})]
            )

            assert len(result) == 1

            return result[0]

        def it_references_the_descriptor_properly(result) -> None:
            assert result["institutionTelephoneNumberTypeDescriptor"] == "uri://ed-fi.org/InstitutionTelephoneNumberTypeDescriptor#Main"

        def it_includes_the_telephone_number(result) -> None:
            assert result["telephoneNumber"] == "(950) 325-9465"
