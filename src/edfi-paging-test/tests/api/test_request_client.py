# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
from time import sleep
from typing import Tuple

import pytest
import requests_mock
from http import HTTPStatus

from edfi_paging_test.api.request_client import RequestClient, timeit
from edfi_paging_test.helpers.argparser import MainArguments
from edfi_paging_test.helpers.output_format import OutputFormat


FAKE_KEY = "TEST_KEY"
FAKE_SECRET = "TEST_SECRET"
FAKE_ENDPOINT = "ENDPOINT"
API_BASE_URL = "https://localhost:54746"
OAUTH_URL = "https://localhost:54746/oauth/token/"
VERSION_INFO = {
     "version": "a",
     "apiMode": "b",
     "dataModels": "c",
     "urls": {
         "oauth": "https://localhost:54746/oauth/token/"
     }
}
FAKE_API_RESPONSE_PAGE1 = [{"id": "a"}, {"id": "b"}]
FAKE_API_RESPONSE_PAGE2 = [{"id": "c"}, {"id": "d"}]
PAGE_SIZE = 2
NUMBER_OF_PAGES = 2
TOTAL_COUNT = 4
TOKEN = "038f4cb947c04fb4851fc3792c6b004f"
TOKEN_RESPONSE = {
    "access_token": "038f4cb947c04fb4851fc3792c6b004f",
    "expires_in": 1800,
    "token_type": "bearer",
}


def describe_testing_RequestClient_class():
    @pytest.fixture()
    def default_request_client():
        args = MainArguments(
            API_BASE_URL,
            1,
            FAKE_KEY,
            FAKE_SECRET,
            "doesn't matter",
            "description",
            OutputFormat.CSV,
            [],
            PAGE_SIZE,
        )
        return RequestClient(args)

    def describe_when_constructing_instance():
        def it_sets_base_url(default_request_client: RequestClient) -> None:
            assert default_request_client.api_base_url == API_BASE_URL

        def it_sets_page_size(default_request_client: RequestClient) -> None:
            assert default_request_client.page_size == PAGE_SIZE

    def describe_when_build_query_params_for_page_method_is_called():
        def describe_given_correct_parameter():
            def it_builds_url_correctly_for_first_page(default_request_client):
                # Arrange
                resource_name = "resource"
                expected_result = "/data/v3/ed-fi/resource"

                # Act
                result = default_request_client._build_url_for_resource(resource_name)

                # Assert
                assert result == expected_result

            def it_builds_url_correctly_for_fifth_page(default_request_client):
                # Arrange
                items_per_page = 17
                expected_result = "offset=68&limit=17"

                # Act
                result = default_request_client._build_query_params_for_page(
                    5, items_per_page
                )

                # Assert
                assert result == expected_result

    def describe_when_getting_results():
        def describe_given_there_is_one_result_page():
            def it_returns_the_page(default_request_client: RequestClient):
                CONTENT = '[{"id":"b"}]'

                # Arrange
                with requests_mock.Mocker() as m:
                    expected_url = API_BASE_URL + "/" + FAKE_ENDPOINT
                    m.post(OAUTH_URL, status_code=201, text=json.dumps(TOKEN_RESPONSE))
                    m.get(expected_url, status_code=HTTPStatus.OK, text=CONTENT)
                    m.get(API_BASE_URL, status_code=HTTPStatus.OK, text=json.dumps(VERSION_INFO))

                    # Act
                    relative_url = "/" + FAKE_ENDPOINT
                    result = default_request_client._get(relative_url)

                    # Assert
                    assert result.text == CONTENT

    def describe_when_getting_total_count():
        def describe_given_there_is_total_count_in_the_header():
            def it_returns_the_total_count(default_request_client: RequestClient):
                # Arrange
                with requests_mock.Mocker() as m:
                    expected_url = API_BASE_URL + "/data/v3/ed-fi/" + FAKE_ENDPOINT + "?offset=0&limit=0&totalCount=true"

                    m.get(API_BASE_URL, status_code=HTTPStatus.OK, text=json.dumps(VERSION_INFO))
                    m.post(OAUTH_URL, status_code=201, text=json.dumps(TOKEN_RESPONSE))
                    m.get(
                        expected_url,
                        status_code=HTTPStatus.OK,
                        headers={"total-count": "2"},
                    )
                    # Act
                    result = default_request_client.get_total(FAKE_ENDPOINT)

                    # Assert
                    assert result == 2

    def describe_when_getting_all_pages():
        def it_should_return_all_available_items(default_request_client: RequestClient):
            with requests_mock.Mocker() as m:
                m.get(API_BASE_URL, status_code=HTTPStatus.OK, text=json.dumps(VERSION_INFO))
                m.post(OAUTH_URL, status_code=201, text=json.dumps(TOKEN_RESPONSE))
                m.get(
                    "https://localhost:54746/data/v3/ed-fi/ENDPOINT?offset=0&limit=2",
                    status_code=HTTPStatus.OK,
                    text=json.dumps(FAKE_API_RESPONSE_PAGE1),
                )
                m.get(
                    "https://localhost:54746/data/v3/ed-fi/ENDPOINT?offset=2&limit=2",
                    status_code=HTTPStatus.OK,
                    text=json.dumps(FAKE_API_RESPONSE_PAGE2),
                )
                m.get(
                    "https://localhost:54746/data/v3/ed-fi/ENDPOINT?offset=4&limit=2",
                    status_code=HTTPStatus.OK,
                    text="[]",
                )
                result = default_request_client.get_all(FAKE_ENDPOINT)

                assert len(result) == TOTAL_COUNT

    def describe_when_get_method_is_called():
        def describe_given_error_occurs():
            def it_continues_normal_operation(default_request_client):
                expected_url = API_BASE_URL + "/" + FAKE_ENDPOINT

                with requests_mock.Mocker() as m:
                    # Arrange
                    m.get(
                        API_BASE_URL,
                        status_code=HTTPStatus.OK,
                        text=json.dumps(VERSION_INFO)
                        )
                    m.post(
                        OAUTH_URL,
                        status_code=HTTPStatus.CREATED,
                        text=json.dumps(TOKEN_RESPONSE),
                    )
                    m.get(
                        expected_url,
                        status_code=HTTPStatus.BAD_REQUEST,
                        text='{"error":"something bad"}',
                    )

                    # Act
                    relative_url = "/" + FAKE_ENDPOINT
                    response = default_request_client._get(relative_url)

                    # Assert
                    assert response.status_code == HTTPStatus.BAD_REQUEST


def describe_when_timing_a_callback():
    RESPONSE = {"a": "b"}
    SLEEP_TIME = 0.1

    def callback() -> dict:
        sleep(SLEEP_TIME)
        return RESPONSE

    @pytest.fixture
    def time_response() -> Tuple[float, dict]:
        return timeit(callback)

    def it_returns_measured_time(time_response: Tuple[float, dict]):
        assert time_response[0] > SLEEP_TIME
        # Just confirm it is very close to the sleep time.
        assert time_response[0] < SLEEP_TIME * 1.1

    def it_returns_callback_response(time_response: Tuple[float, dict]):
        assert time_response[1] == RESPONSE
