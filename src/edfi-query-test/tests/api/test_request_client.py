# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
from http import HTTPStatus
from unittest.mock import patch, Mock

import pytest
import requests_mock

from edfi_query_test.api.request_client import RequestClient, timeit
from edfi_query_test.helpers.main_arguments import MainArguments
from edfi_query_test.helpers.output_format import OutputFormat
from edfi_query_test.helpers.log_level import LogLevel


FAKE_KEY = "TEST_KEY"
FAKE_SECRET = "TEST_SECRET"
API_BASE_URL = "https://localhost:54746"
OAUTH_URL = "https://localhost:54746/oauth/token/"
VERSION_INFO = {
    "version": "a",
    "apiMode": "b", 
    "dataModels": "c",
    "urls": {
        "oauth": "https://localhost:54746/oauth/token/",
        "dataManagementApi": "https://localhost:54746/data/v3/"
    }
}
FAKE_API_RESPONSE = [{"id": "123", "studentUniqueId": "student1"}]
TOKEN_RESPONSE = {
    "access_token": "038f4cb947c04fb4851fc3792c6b004f",
    "expires_in": 1800,
    "token_type": "bearer",
}


@pytest.fixture()
def default_request_client():
    args = MainArguments(
        baseUrl=API_BASE_URL,
        key=FAKE_KEY,
        secret=FAKE_SECRET,
        ignoreCertificateErrors=True,
        connectionLimit=5,
        output="./output",
        contentType=OutputFormat.CSV,
        resourceList=["Students"],
        pageSize=100,
        description="Test run",
        log_level=LogLevel.INFO
    )
    return RequestClient(args)


def describe_testing_RequestClient_class():
    def describe_when_constructing_instance():
        def it_sets_base_url(default_request_client):
            assert default_request_client.api_base_url == API_BASE_URL

        def it_sets_page_size(default_request_client):
            assert default_request_client.page_size == 100

        def it_sets_verify_cert(default_request_client):
            assert default_request_client.verify_cert is False

    def describe_when_querying_resources():
        def it_constructs_query_url_correctly(default_request_client):
            with requests_mock.Mocker() as m:
                # Setup API version and OAuth mocks
                m.get(API_BASE_URL, json=VERSION_INFO)
                m.post(OAUTH_URL, json=TOKEN_RESPONSE)
                
                # Mock the actual query request
                expected_url = f"{API_BASE_URL}/data/v3/ed-fi/students?limit=1&studentUniqueId=student1&schoolId=123"
                m.get(expected_url, json=FAKE_API_RESPONSE)
                
                # Act
                result = default_request_client.query("students", {"studentUniqueId": "student1", "schoolId": "123"})
                
                # Assert
                assert result == FAKE_API_RESPONSE

        def it_url_encodes_query_parameters(default_request_client):
            with requests_mock.Mocker() as m:
                # Setup API version and OAuth mocks
                m.get(API_BASE_URL, json=VERSION_INFO)
                m.post(OAUTH_URL, json=TOKEN_RESPONSE)
                
                # Mock query with special characters
                query_value = "test value with spaces"
                expected_url = f"{API_BASE_URL}/data/v3/ed-fi/students?limit=1&name=test%20value%20with%20spaces"
                m.get(expected_url, json=FAKE_API_RESPONSE)
                
                # Act
                result = default_request_client.query("students", {"name": query_value})
                
                # Assert
                assert result == FAKE_API_RESPONSE

    def describe_when_getting_all_data():
        def it_retrieves_all_pages(default_request_client):
            with requests_mock.Mocker() as m:
                # Setup API version and OAuth mocks
                m.get(API_BASE_URL, json=VERSION_INFO)
                m.post(OAUTH_URL, json=TOKEN_RESPONSE)
                
                # Mock paginated responses
                page1_response = [{"id": "1"}, {"id": "2"}]
                page2_response = [{"id": "3"}]
                
                # First request returns 2 items (indicating more pages)
                m.get(f"{API_BASE_URL}/data/v3/ed-fi/students?offset=0&limit=100", 
                      json=page1_response, 
                      headers={"Total-Count": "3"})
                      
                # Second request returns remaining item
                m.get(f"{API_BASE_URL}/data/v3/ed-fi/students?offset=100&limit=100", 
                      json=page2_response,
                      headers={"Total-Count": "3"})
                
                # Act
                result = default_request_client.get_all("students")
                
                # Assert
                assert len(result) == 3
                assert result[0]["id"] == "1"
                assert result[1]["id"] == "2" 
                assert result[2]["id"] == "3"

        def it_handles_single_page_response(default_request_client):
            with requests_mock.Mocker() as m:
                # Setup API version and OAuth mocks
                m.get(API_BASE_URL, json=VERSION_INFO)
                m.post(OAUTH_URL, json=TOKEN_RESPONSE)
                
                # Mock single page response (less than page size, so no more pages expected)
                single_page_response = [{"id": "1"}]
                m.get(f"{API_BASE_URL}/data/v3/ed-fi/students?offset=0&limit=100", 
                      json=single_page_response,
                      headers={"Total-Count": "1"})
                
                # Mock second page request that won't be called (due to small first page)
                m.get(f"{API_BASE_URL}/data/v3/ed-fi/students?offset=100&limit=100", 
                      json=[],
                      headers={"Total-Count": "1"})
                
                # Act
                result = default_request_client.get_all("students")
                
                # Assert
                assert len(result) == 1
                assert result[0]["id"] == "1"

    def describe_when_handling_authentication():
        def it_obtains_oauth_token(default_request_client):
            with requests_mock.Mocker() as m:
                # Setup mocks
                m.get(API_BASE_URL, json=VERSION_INFO)
                m.post(OAUTH_URL, json=TOKEN_RESPONSE)
                m.get(f"{API_BASE_URL}/data/v3/ed-fi/students", json=FAKE_API_RESPONSE)
                
                # Act - This will trigger authentication
                result = default_request_client.get_all("students")
                
                # Assert - Verify OAuth request was made
                oauth_requests = [req for req in m.request_history if req.url.endswith('/oauth/token/')]
                assert len(oauth_requests) == 1
                
                oauth_request = oauth_requests[0]
                assert oauth_request.method == 'POST'


def describe_when_timing_a_callback():
    def it_returns_measured_time():
        # Arrange
        def test_callback():
            return "result"
        
        # Act
        elapsed_time, result = timeit(test_callback)
        
        # Assert
        assert elapsed_time >= 0
        assert result == "result"

    def it_returns_callback_response():
        # Arrange
        expected_result = {"test": "data"}
        def test_callback():
            return expected_result
        
        # Act
        elapsed_time, result = timeit(test_callback)
        
        # Assert
        assert result == expected_result