# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any, Dict


class PaginatedResult():
    """
    The PaginatedResult class is bound with information from the response of the
    api, specifically when it returns a list of items that could be paginated.

    Parameters
    ----------
    request_client : RequestClient
        The request client.
    page_size : int
        The number of items per page.
    total_count : int
        Total number of items.
    api_response : dict
        The original response as a dictionary.
    resource_name : str
        The name used by the API for the current resource.
    current_page : Optional[str]
        The page that you have requested.
    """

    def __init__(
        self,
        resource_name: str,
        page_size: int,
        api_response: Dict[str, Any],
        current_page: int = 1,
    ):
        self.page_size = page_size
        self.current_page = current_page

        if api_response is None:
            self._current_page_items: Dict[str, Any] = []
        else:
            self._current_page_items = api_response

        self._api_response = api_response
        self._resource_name = resource_name

    @property
    def current_page_items(self) -> Dict[str, Any] :
        return self._current_page_items

    @property
    def is_empty(self) -> bool :
        return len(self._current_page_items) == 0
