# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import pytest

import requests_mock

from edfi_paging_test.api.request_client import RequestClient
from http import HTTPStatus


FAKE_KEY = "TEST_KEY"
FAKE_SECRET = "TEST_SECRET"
FAKE_ENDPOINT = "/ENDPOINT"
API_BASE_URL = "https://localhost:54746"
OAUTH_URL = "https://localhost:54746/oauth/token/"
PAGE_SIZE = 10
RETRY_COUNT = 0
TOKEN = "038f4cb947c04fb4851fc3792c6b004f"
TOKEN_RESPONSE = {
  "access_token": "038f4cb947c04fb4851fc3792c6b004f",
  "expires_in": 1800,
  "token_type": "bearer"
}


def describe_testing_RequestClient_class():
    @pytest.fixture()
    def default_request_client():
        return RequestClient(api_base_url=API_BASE_URL, api_key=FAKE_KEY, api_secret=FAKE_SECRET, page_size=PAGE_SIZE, retry_count=RETRY_COUNT)

    def describe_when_constructing_instance():

        def it_sets_base_url(default_request_client: RequestClient) -> None:
            assert default_request_client.api_base_url == API_BASE_URL

        def it_sets_api_key(default_request_client: RequestClient) -> None:
            assert default_request_client.api_key == FAKE_KEY

        def it_sets_api_secret(default_request_client: RequestClient) -> None:
            assert default_request_client.api_secret == FAKE_SECRET

        def it_sets_connection_limit(default_request_client: RequestClient) -> None:
            assert default_request_client.retry_count == RETRY_COUNT

        def it_sets_output_dir(default_request_client: RequestClient) -> None:
            assert default_request_client.page_size == PAGE_SIZE

    def describe_when_build_query_params_for_page_method_is_called():
        def describe_given_correct_parameter():
            def it_builds_url_correctly_for_first_page(default_request_client):
                # Arrange
                resource_name = "resource"
                expected_result = "/data/v3/ed-fi/resource"

                # Act
                result = default_request_client.build_url_for_resource(
                   resource_name
                )

                # Assert
                assert result == expected_result

            def it_builds_url_correctly_for_fifth_page(default_request_client):
                # Arrange
                items_per_page = 17
                expected_result = "offset=68&limit=17"

                # Act
                result = default_request_client.build_query_params_for_page(
                    5,
                    items_per_page
                )

                # Assert
                assert result == expected_result

            def it_builds_url_correctly_for_total_count(default_request_client):
                # Arrange
                expected_result = "offset=0&limit=0&totalCount=true"

                # Act
                result = default_request_client.build_query_params_for_total_count()

                # Assert
                assert result == expected_result

    def describe_when_get_method_is_called():
        def describe_given_error_occurs():
            def it_raises_an_error(default_request_client):
                expected_url = API_BASE_URL + FAKE_ENDPOINT

                with pytest.raises(RuntimeError):
                    with requests_mock.Mocker() as m:
                        # Arrange
                        m.post(OAUTH_URL, status_code=201, text=json.dumps(TOKEN_RESPONSE))
                        m.get(expected_url, status_code=HTTPStatus.BAD_REQUEST, text="{\"error\":\"something bad\"}")

                        # Act
                        default_request_client.get(FAKE_ENDPOINT)

    def describe_when_getting_results():
        def describe_given_there_is_one_result_page():
            def it_returns_the_page(default_request_client):
                # Arrange
                with requests_mock.Mocker() as m:
                    expected_url = API_BASE_URL + FAKE_ENDPOINT
                    m.post(OAUTH_URL, status_code=201, text=json.dumps(TOKEN_RESPONSE))
                    m.get(expected_url, status_code=HTTPStatus.OK, text="[{\"id\":\"b\"}]")
                    # Act
                    result = default_request_client.get(FAKE_ENDPOINT)

                    # Assert
                    assert result[0]["id"] == "b"

    def describe_when_getting_total_count():
        def describe_given_there_is_total_count_in_the_header():
            def it_returns_the_total_count(default_request_client):
                # Arrange
                with requests_mock.Mocker() as m:
                    expected_url = API_BASE_URL + FAKE_ENDPOINT
                    m.post(OAUTH_URL, status_code=201, text=json.dumps(TOKEN_RESPONSE))
                    m.get(expected_url, status_code=HTTPStatus.OK, headers={'total-count' : '2'})
                    # Act
                    result = default_request_client.get_total(FAKE_ENDPOINT)

                    # Assert
                    assert result == 2
