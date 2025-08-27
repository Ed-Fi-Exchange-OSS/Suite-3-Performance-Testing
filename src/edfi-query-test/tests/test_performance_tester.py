# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict, Any, List
import pytest

from edfi_query_test.performance_tester import (
    find_resource_with_all_query_params,
    flatten_resource,
    get_query_params_combinations,
    capitalize_first,
    invalid_resources
)
from edfi_query_test.helpers.query_param import QueryParam


def describe_capitalize_first():
    def describe_when_given_various_strings():
        def it_capitalizes_first_letter():
            assert capitalize_first("hello") == "Hello"

        def it_handles_single_character():
            assert capitalize_first("a") == "A"

        def it_preserves_rest_of_string():
            assert capitalize_first("hELLO") == "HELLO"

        def it_handles_already_capitalized():
            assert capitalize_first("Hello") == "Hello"


def describe_invalid_resources():
    def describe_when_comparing_resource_lists():
        def it_finds_missing_resources():
            # Arrange
            openapi_resources = ["students", "schools", "staff"]
            resources_to_check = ["students", "schools", "teachers", "courses"]
            
            # Act
            result = invalid_resources(openapi_resources, resources_to_check)
            
            # Assert
            assert "teachers" in result
            assert "courses" in result
            assert "students" not in result
            assert "schools" not in result

        def it_returns_empty_when_all_found():
            # Arrange
            openapi_resources = ["students", "schools", "staff"]
            resources_to_check = ["students", "schools"]
            
            # Act
            result = invalid_resources(openapi_resources, resources_to_check)
            
            # Assert
            assert result == []


def describe_flatten_resource():
    def describe_when_resource_has_nested_objects():
        def it_flattens_reference_objects():
            # Arrange
            resource = {
                "studentUniqueId": "123",
                "schoolReference": {
                    "schoolId": "456"
                },
                "simpleField": "value"
            }
            
            # Act
            result = flatten_resource(resource)
            
            # Assert
            assert result["studentUniqueId"] == "123"
            assert result["simpleField"] == "value"
            assert result["schoolId"] == "456"  # Flattened from schoolReference
            assert "schoolReference" not in result

        def it_handles_non_reference_nested_objects():
            # Arrange
            resource = {
                "studentUniqueId": "123",
                "address": {
                    "streetNumber": "100",
                    "city": "Austin"
                }
            }
            
            # Act
            result = flatten_resource(resource)
            
            # Assert
            assert result["studentUniqueId"] == "123"
            assert result["addressStreetNumber"] == "100"
            assert result["addressCity"] == "Austin"
            assert "address" not in result

        def it_handles_resource_without_nested_objects():
            # Arrange
            resource = {
                "studentUniqueId": "123",
                "firstName": "John",
                "lastName": "Doe"
            }
            
            # Act
            result = flatten_resource(resource)
            
            # Assert
            assert result == resource

        def it_handles_empty_resource():
            # Act
            result = flatten_resource({})
            
            # Assert
            assert result == {}


def describe_get_query_params_combinations():
    def describe_when_given_query_parameters():
        def it_generates_all_combinations_up_to_size_6():
            # Arrange
            params = [
                QueryParam("param1"),
                QueryParam("param2"),
                QueryParam("param3")
            ]
            
            # Act
            result = get_query_params_combinations(params)
            
            # Assert
            # Should have combinations of size 1, 2, and 3
            # Size 1: 3 combinations
            # Size 2: 3 combinations  
            # Size 3: 1 combination
            # Total: 7 combinations
            assert len(result) == 7
            
            # Check that we have single param combinations
            single_param_combos = [combo for combo in result if len(combo) == 1]
            assert len(single_param_combos) == 3
            
            # Check that we have two param combinations
            two_param_combos = [combo for combo in result if len(combo) == 2]
            assert len(two_param_combos) == 3
            
            # Check that we have three param combination
            three_param_combos = [combo for combo in result if len(combo) == 3]
            assert len(three_param_combos) == 1

        def it_handles_single_parameter():
            # Arrange
            params = [QueryParam("param1")]
            
            # Act
            result = get_query_params_combinations(params)
            
            # Assert
            assert len(result) == 1
            assert len(result[0]) == 1
            assert result[0][0].name == "param1"

        def it_handles_empty_parameter_list():
            # Act
            result = get_query_params_combinations([])
            
            # Assert
            assert result == []


def describe_find_resource_with_all_query_params():
    def describe_when_searching_for_matching_resources():
        def it_finds_resources_with_all_params():
            # Arrange
            resources = [
                {"studentUniqueId": "123", "schoolId": "456", "gradeLevel": "1"},
                {"studentUniqueId": "124", "schoolId": None, "gradeLevel": "2"},  # Missing schoolId
                {"studentUniqueId": "125", "schoolId": "457", "gradeLevel": "1"},
                {"firstName": "John", "schoolId": "456"}  # Missing studentUniqueId
            ]
            query_params = (QueryParam("studentUniqueId"), QueryParam("schoolId"))
            count = 10
            
            # Act
            result = find_resource_with_all_query_params(resources, query_params, count)
            
            # Assert
            assert len(result) == 2  # Only first and third resources match
            assert result[0]["studentUniqueId"] == "123"
            assert result[1]["studentUniqueId"] == "125"

        def it_respects_count_limit():
            # Arrange
            resources = [
                {"studentUniqueId": "123", "schoolId": "456"},
                {"studentUniqueId": "124", "schoolId": "457"},
                {"studentUniqueId": "125", "schoolId": "458"},
            ]
            query_params = (QueryParam("studentUniqueId"),)
            count = 2
            
            # Act
            result = find_resource_with_all_query_params(resources, query_params, count)
            
            # Assert
            assert len(result) == 2

        def it_handles_no_matching_resources():
            # Arrange
            resources = [
                {"firstName": "John", "lastName": "Doe"},
                {"address": "123 Main St", "city": "Austin"}
            ]
            query_params = (QueryParam("studentUniqueId"), QueryParam("schoolId"))
            count = 10
            
            # Act
            result = find_resource_with_all_query_params(resources, query_params, count)
            
            # Assert
            assert result == []

        def it_excludes_resources_with_null_values():
            # Arrange
            resources = [
                {"studentUniqueId": "123", "schoolId": "456"},
                {"studentUniqueId": None, "schoolId": "457"},  # Null studentUniqueId
                {"studentUniqueId": "125", "schoolId": None}   # Null schoolId
            ]
            query_params = (QueryParam("studentUniqueId"), QueryParam("schoolId"))
            count = 10
            
            # Act
            result = find_resource_with_all_query_params(resources, query_params, count)
            
            # Assert
            assert len(result) == 1
            assert result[0]["studentUniqueId"] == "123"

        def it_handles_empty_resource_list():
            # Arrange
            query_params = (QueryParam("studentUniqueId"),)
            count = 10
            
            # Act
            result = find_resource_with_all_query_params([], query_params, count)
            
            # Assert
            assert result == []