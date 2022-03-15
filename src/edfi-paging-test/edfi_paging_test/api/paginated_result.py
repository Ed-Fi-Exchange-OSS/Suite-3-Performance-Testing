# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any, Dict, List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from edfi_paging_test.api.request_client import RequestClient


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
    Attributes
    ----------
    current_page_items : Dict[str, Any]
        The list of items for the current page.
    """

    def __init__(
        self,
        request_client: "RequestClient",
        resource_name: str,
        page_size: int,
        total_count: int,
        api_response: Dict[str, Any],
        current_page: int = 1,
    ):
        self.request_client = request_client
        self.page_size = page_size
        self.current_page = current_page
        self.total_count = total_count

        if api_response is None:
            self.current_page_items: Dict[str, Any] = []
        else:
            self.current_page_items = api_response

        self._api_response = api_response
        self._resource_name = resource_name

    def get_next_page(self) -> Optional['PaginatedResult']:
        """Send an HTTP GET request for the next page.
        Returns
        -------
        Optional[PaginatedResult]
            If there are more pages, this method will send a get request
            in order to get the elements for the next page.
        """

        self.current_page = self.current_page + 1
        next_url = f"{self.request_client.build_url_for_resource(self._resource_name)}?{self.request_client.build_query_params_for_page(self.current_page, self.page_size)}"
        response = self.request_client.get(next_url)

        self._api_response = response
        if len(self._api_response) == 0:
            return None
        else:
            self.current_page_items = self._api_response
        return self

    def get_all_pages(self) -> List[Any]:
        """
        Returns all items from the PaginatedResult object within all available pages
        Returns
        -------
        list
            A list of all parsed results
        """

        items: List[Any] = []
        while True:
            items = items + list(self.current_page_items)
            if self.get_next_page() is None:
                break

        return items
