# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

# from unittest.mock import Mock
import pytest

from edfi_paging_test.api.paginated_result import PaginatedResult

FAKE_KEY = "TEST_KEY"
FAKE_SECRET = "TEST_SECRET"
FAKE_ENDPOINT_URL = "FAKE_URL"
API_BASE_URL = "http://localhost:54746"
FAKE_RESOURCE_NAME = "resource_name"
FAKE_API_RESPONSE_PAGE1 = [{"id" : "a"}, {"id" : "b"}]
PAGE_SIZE = 2
STATUS_CODE = 200


@pytest.fixture
def default_paginated_result():
    paginated_result = PaginatedResult(
        page_size=PAGE_SIZE,
        api_response=FAKE_API_RESPONSE_PAGE1,
        resource_name=FAKE_RESOURCE_NAME,
        status_code=STATUS_CODE
    )
    return paginated_result


@pytest.fixture
def empty_paginated_result():
    paginated_result = PaginatedResult(
        page_size=PAGE_SIZE,
        api_response=[],
        resource_name=FAKE_RESOURCE_NAME,
        status_code=STATUS_CODE
    )
    return paginated_result


def describe_testing_PaginatedResult_class():
    def describe_when_constructing():
        def it_sets_correct_properties(default_paginated_result):

            # Assert
            assert default_paginated_result.page_size == PAGE_SIZE
            assert default_paginated_result._resource_name == FAKE_RESOURCE_NAME
            assert default_paginated_result.current_page == 1
            assert len(default_paginated_result.current_page_items) != 0

        def describe_given_resource_list_present_in_api_response():
            def it_binds_current_page_items(default_paginated_result):

                # Assert
                assert default_paginated_result.current_page_items[0] == FAKE_API_RESPONSE_PAGE1[0]

            def it_returns_correct_size(default_paginated_result):

                # Assert
                assert default_paginated_result.size == 2

        def describe_given_items_not_present_in_api_response():
            def it_returns_correct_size(empty_paginated_result):

                # Assert
                assert empty_paginated_result.size == 0
