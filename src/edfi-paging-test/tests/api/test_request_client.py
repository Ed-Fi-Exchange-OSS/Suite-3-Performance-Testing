# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest
import os

# from edfi_paging_test.api.paginated_result import PaginatedResult
from edfi_paging_test.api.request_client import RequestClient
# from unittest.mock import MagicMock
from unittest.mock import patch

FAKE_KEY = "TEST_KEY"
FAKE_SECRET = "TEST_SECRET"
FAKE_ENDPOINT_URL = "FAKE_URL"
API_BASE_URL = "http://localhost:54746"
PAGE_SIZE = 10
RETRY_COUNT = 0


@patch.dict(os.environ, {"OAUTHLIB_INSECURE_TRANSPORT": "1"})
def describe_testing_RequestClient_class():
    @pytest.fixture
    def default_request_client():
        return RequestClient(api_base_url=API_BASE_URL, api_key=FAKE_KEY, api_secret=FAKE_SECRET, page_size=PAGE_SIZE, retry_count=RETRY_COUNT)

    class MockOAuth(object):
        authorized = True

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


"""     def describe_when_get_method_is_called():
        def describe_given_error_occurs():
            def it_raises_an_HTTPError(requests_mock, default_request_client):
                expected_url = API_BASE_URL + FAKE_ENDPOINT_URL

                # Arrange
                default_request_client.oauth =  MagicMock(return_value=MockOAuth())
                requests_mock.get(
                    expected_url, reason="BadRequest", status_code=400, text="no good"
                )

                # Act
                try:
                    default_request_client.get(FAKE_ENDPOINT_URL)
                    raise RuntimeError("expected an error to occur")
                except RuntimeError as ex:
                    assert str(ex) == "BadRequest (400): no good"

    def describe_when_getting_results():
        def describe_given_there_is_one_result_page():
            def it_returns_the_page(default_request_client, requests_mock):
                page_size = 435
                expected_url_1 = "http://localhost:54746/data/v3/ed-fi/studentSectionAttendanceEvents?offset=0&limit=435"

                # Arrange
                resource = "studentSectionAttendanceEvents"
                text = '[{"id":"b"}]'
                default_request_client.oauth =  MagicMock(return_value=MockOAuth())
                requests_mock.get(
                     expected_url_1, reason="OK", status_code=200, text=text
                )

                # Act
                result = default_request_client.get(resource)

                assert result.get_all_pages()[0]["id"] == "b"


        def describe_given_two_pages_of_results():
            @pytest.fixture
            def result(default_request_client, requests_mock):
                section_id = 3324
                page_size = 1
                expected_url_1 = "http://localhost:54746/data/v3/ed-fi/studentSectionAttendanceEvents?offset=0&limit=1"
                expected_url_2 = "http://localhost:54746/data/v3/ed-fi/studentSectionAttendanceEvents?offset=1&limit=1"

                # Arrange
                text_1 = '{[{"id":"b"}]}'
                text_2 = '{[{"id":"c"}]}'

                def callback(request, context):
                    if request.url == expected_url_1:
                        return text_1
                    else:
                        return text_2

                requests_mock.get(
                    expected_url_1, reason="OK", status_code=200, text=callback
                )
                requests_mock.get(
                    expected_url_2, reason="OK", status_code=200, text=callback
                )

                # Act
                result = default_request_client.get_all(section_id, page_size)

                return result

            def it_should_return_two_result_pages(result: PaginatedResult, requests_mock):
                assert result.get_next_page() is not None

            def it_should_contain_first_result(
                result: PaginatedResult, requests_mock
            ):
                assert (
                    len([r for r in result.current_page_items if r["id"] == "b"]) == 1
                )

            def it_should_contain_second_result(result, requests_mock):
                assert (
                    len(
                        [
                            r
                            for r in result.get_next_page().current_page_items
                            if r["id"] == "c"
                        ]
                    )
                    == 1
                )
 """
