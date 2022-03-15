# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# from unittest.mock import Mock
import pytest

from edfi_paging_test.api.paginated_result import PaginatedResult
from edfi_paging_test.api.request_client import RequestClient

FAKE_KEY = "TEST_KEY"
FAKE_SECRET = "TEST_SECRET"
FAKE_ENDPOINT_URL = "FAKE_URL"
API_BASE_URL = "http://localhost:54746"
FAKE_RESOURCE_NAME = "resource_name"
FAKE_API_RESPONSE_PAGE1 = [{"id" : "a"}, {"id" : "b"}]
FAKE_API_RESPONSE_PAGE2 = [{"id" : "c"}, {"id" : "d"}]
PAGE_SIZE = 2
TOTAL_COUNT = 4


@pytest.fixture
def default_request_client(mocker):
    request_client = RequestClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET, api_base_url=API_BASE_URL)
    request_client.get = mocker.MagicMock(return_value=FAKE_API_RESPONSE_PAGE2)
    return request_client


@pytest.fixture
def default_paginated_result(default_request_client, mocker):
    return PaginatedResult(
        request_client=default_request_client,
        page_size=PAGE_SIZE,
        api_response=FAKE_API_RESPONSE_PAGE1,
        resource_name=FAKE_RESOURCE_NAME,
        total_count=TOTAL_COUNT
    )


@pytest.fixture
def last_page_request_client(mocker):
    request_client = RequestClient(api_key=FAKE_KEY, api_secret=FAKE_SECRET, api_base_url=API_BASE_URL)
    request_client.get = mocker.MagicMock(return_value=None)
    return request_client


@pytest.fixture
def last_page_paginated_result(default_request_client, mocker):
    return PaginatedResult(
        request_client=last_page_request_client,
        page_size=PAGE_SIZE,
        api_response=FAKE_API_RESPONSE_PAGE1,
        resource_name=FAKE_RESOURCE_NAME,
        total_count=TOTAL_COUNT
    )


def describe_testing_PaginatedResult_class():
    def describe_when_constructing():
        def it_sets_correct_properties(default_paginated_result):

            # Assert
            assert default_paginated_result.page_size == PAGE_SIZE
            assert default_paginated_result._resource_name == FAKE_RESOURCE_NAME
            assert default_paginated_result.current_page == 1
            assert len(default_paginated_result.current_page_items) == 2
            assert default_paginated_result.total_count == TOTAL_COUNT


"""
    def describe_when_calling_get_next_page():
        def describe_given_items_present_in_api_response():
            def it_returns_paginated_result(default_paginated_result):

                # Act
                result = default_paginated_result.get_next_page()

                # Assert
                assert isinstance(result, PaginatedResult)

        def describe_given_items_not_present_in_api_response():
            def it_returns_None(last_page_paginated_result):

                # Act
                result = last_page_paginated_result.get_next_page()

                # Assert
                assert result is None

        def describe_given_resource_name_key_present_in_api_response():
            def it_binds_current_page_items(mocker, default_paginated_result):

                # Arrange
                FAKE_API_RESPONSE = {FAKE_RESOURCE_NAME: [{"test": "test"}]}
                default_paginated_result.request_client.get = mocker.MagicMock(
                    return_value=FAKE_API_RESPONSE
                )

                # Act
                default_paginated_result.get_next_page()

                # Assert
                assert len(default_paginated_result.current_page_items) == 1

        def describe_given_links_and_next_key_not_present_in_api_response():
            def it_returns_None(default_paginated_result):

                # Arrange
                default_paginated_result._api_response = dict()

                # Act
                result = default_paginated_result.get_next_page()

                # Assert
                assert result is None


def describe_when_getting_all_pages():
    @pytest.fixture
    def paginated_result():
        request_client = Mock(spec=RequestClient)
        page_size = 22

        users = {
            "user": [{"uid": 1234, "role_id": 321}],
            "total": 1,
            "links": {"self": "ignore"},
        }
        paginated_result = PaginatedResult(
            request_client, page_size, users, "user", "ignore me"
        )
        paginated_result.get_next_page = Mock(return_value=None)

        # act
        paginated_result.get_all_pages()
        return paginated_result

    def it_should_call_get_next_page(paginated_result):
        assert paginated_result.get_next_page.called

    @pytest.fixture
    def result():
        request_client = Mock(spec=RequestClient)
        page_size = 22

        users = {
            "user": [{"uid": 1234, "role_id": 321}],
            "total": 1,
            "links": {"self": "ignore"},
        }
        paginated_result = PaginatedResult(
            request_client, page_size, users, "user", "ignore me"
        )

        # act
        return paginated_result.get_all_pages()

    def it_should_return_all_available_items(result: list):
        assert len(result) == 1
 """
