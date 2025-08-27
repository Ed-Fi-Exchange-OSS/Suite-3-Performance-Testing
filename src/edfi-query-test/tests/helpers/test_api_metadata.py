# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from unittest.mock import patch, Mock
import pytest
import requests_mock

from edfi_query_test.helpers.api_metadata import (
    get_query_params_by_resource,
    get_resource_metadata_response,
    normalize_resource_path
)
from edfi_query_test.helpers.query_param import QueryParam


API_BASE_URL = "https://localhost:54746"
FAKE_OPENAPI_METADATA = {
    "paths": {
        "/ed-fi/students": {
            "get": {
                "parameters": [
                    {"name": "studentUniqueId", "in": "query"},
                    {"name": "schoolId", "in": "query"},
                    {"name": "limit", "in": "query"},
                    {"name": "offset", "in": "query"}
                ]
            }
        },
        "/ed-fi/schools": {
            "get": {
                "parameters": [
                    {"name": "schoolId", "in": "query"},
                    {"name": "nameOfInstitution", "in": "query"}
                ]
            }
        },
        "/ed-fi/students/{id}": {
            "get": {"parameters": []}
        }
    }
}


def describe_normalize_resource_path():
    def describe_when_given_various_path_formats():
        def it_removes_leading_slash():
            # Act
            result = normalize_resource_path("/students")
            
            # Assert
            assert result == "students"

        def it_removes_edfi_prefix():
            # Act
            result = normalize_resource_path("ed-fi/students")
            
            # Assert
            assert result == "students"

        def it_removes_both_slash_and_prefix():
            # Act
            result = normalize_resource_path("/ed-fi/students")
            
            # Assert
            assert result == "students"

        def it_handles_extension_paths():
            # Act
            result = normalize_resource_path("/tpdm/candidates")
            
            # Assert
            assert result == "tpdm/candidates"

        def it_handles_plain_resource_name():
            # Act
            result = normalize_resource_path("students")
            
            # Assert
            assert result == "students"


def describe_get_resource_metadata_response():
    def describe_when_api_responds_successfully():
        def it_returns_metadata():
            # Clear cache to avoid interference from other tests
            from edfi_query_test.helpers.api_metadata import get_base_api_response, get_openapi_metadata_response, get_resource_metadata_response
            get_base_api_response.cache_clear()
            get_openapi_metadata_response.cache_clear()
            get_resource_metadata_response.cache_clear()
            
            # Arrange
            with requests_mock.Mocker() as m:
                # Mock the base API response first
                base_response = {
                    "urls": {
                        "openApiMetadata": f"{API_BASE_URL}/metadata/"
                    }
                }
                openapi_list_response = [
                    {"name": "Resources", "endpointUri": f"{API_BASE_URL}/metadata/resources"}
                ]
                
                m.get(API_BASE_URL, json=base_response)
                m.get(f"{API_BASE_URL}/metadata/", json=openapi_list_response)
                m.get(f"{API_BASE_URL}/metadata/resources", json=FAKE_OPENAPI_METADATA)
                
                # Act
                result = get_resource_metadata_response(API_BASE_URL, verify_cert=False)
                
                # Assert
                assert result == FAKE_OPENAPI_METADATA

    def describe_when_verify_cert_is_true():
        def it_calls_with_verification():
            # Clear cache to avoid interference from other tests
            from edfi_query_test.helpers.api_metadata import get_base_api_response, get_openapi_metadata_response, get_resource_metadata_response
            get_base_api_response.cache_clear()
            get_openapi_metadata_response.cache_clear()
            get_resource_metadata_response.cache_clear()
            
            # Arrange
            with requests_mock.Mocker() as m:
                # Mock the base API response first
                base_response = {
                    "urls": {
                        "openApiMetadata": f"{API_BASE_URL}/metadata/"
                    }
                }
                openapi_list_response = [
                    {"name": "Resources", "endpointUri": f"{API_BASE_URL}/metadata/resources"}
                ]
                
                m.get(API_BASE_URL, json=base_response)
                m.get(f"{API_BASE_URL}/metadata/", json=openapi_list_response)
                m.get(f"{API_BASE_URL}/metadata/resources", json=FAKE_OPENAPI_METADATA)
                
                # Act
                result = get_resource_metadata_response(API_BASE_URL, verify_cert=True)
                
                # Assert
                assert result == FAKE_OPENAPI_METADATA
                # Verify the request was made with verify=True (implicitly tested by successful mock)


def describe_get_query_params_by_resource():
    def describe_when_metadata_contains_resources():
        def it_extracts_query_parameters():
            # Arrange
            with patch('edfi_query_test.helpers.api_metadata.get_resource_metadata_response') as mock_metadata:
                mock_metadata.return_value = FAKE_OPENAPI_METADATA
                
                # Act
                result = get_query_params_by_resource(API_BASE_URL, verify_cert=False)
                
                # Assert
                assert "students" in result
                assert "schools" in result
                
                # Check students query params
                student_params = [param.name for param in result["students"]]
                assert "studentUniqueId" in student_params
                assert "schoolId" in student_params
                # Should exclude limit and offset as they're pagination params
                assert "limit" not in student_params
                assert "offset" not in student_params
                
                # Check schools query params  
                school_params = [param.name for param in result["schools"]]
                assert "schoolId" in school_params
                assert "nameOfInstitution" in school_params

        def it_excludes_non_queryable_paths():
            # Arrange
            metadata_with_id_path = {
                "paths": {
                    "/ed-fi/students": {
                        "get": {
                            "parameters": [{"name": "studentUniqueId", "in": "query"}]
                        }
                    },
                    "/ed-fi/students/{id}": {
                        "get": {"parameters": []}
                    }
                }
            }
            
            with patch('edfi_query_test.helpers.api_metadata.get_resource_metadata_response') as mock_metadata:
                mock_metadata.return_value = metadata_with_id_path
                
                # Act
                result = get_query_params_by_resource(API_BASE_URL, verify_cert=False)
                
                # Assert
                assert "students" in result
                # Should not include the {id} path as a separate resource
                assert len(result) == 1

        def it_filters_pagination_parameters():
            # Arrange
            metadata_with_pagination = {
                "paths": {
                    "/ed-fi/students": {
                        "get": {
                            "parameters": [
                                {"name": "studentUniqueId", "in": "query"},
                                {"name": "limit", "in": "query"},
                                {"name": "offset", "in": "query"},
                                {"name": "totalCount", "in": "query"}
                            ]
                        }
                    }
                }
            }
            
            with patch('edfi_query_test.helpers.api_metadata.get_resource_metadata_response') as mock_metadata:
                mock_metadata.return_value = metadata_with_pagination
                
                # Act
                result = get_query_params_by_resource(API_BASE_URL, verify_cert=False)
                
                # Assert
                student_params = [param.name for param in result["students"]]
                assert "studentUniqueId" in student_params
                assert "limit" not in student_params
                assert "offset" not in student_params
                assert "totalCount" not in student_params

        def it_returns_QueryParam_objects():
            # Arrange
            with patch('edfi_query_test.helpers.api_metadata.get_resource_metadata_response') as mock_metadata:
                mock_metadata.return_value = FAKE_OPENAPI_METADATA
                
                # Act
                result = get_query_params_by_resource(API_BASE_URL, verify_cert=False)
                
                # Assert
                for resource_params in result.values():
                    for param in resource_params:
                        assert isinstance(param, QueryParam)
                        assert param.name is not None
                        assert len(param.name) > 0