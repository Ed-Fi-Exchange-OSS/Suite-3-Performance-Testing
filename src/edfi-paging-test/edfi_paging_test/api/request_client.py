# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import os
from typing import Any, Dict, List, Optional

from requests import Response
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session  # type: ignore

from edfi_paging_test.api.paginated_result import PaginatedResult
from edfi_paging_test.helpers.argparser import MainArguments
from edfi_paging_test.reporter.measurement import Measurement
from edfi_paging_test.reporter.request_logger import log_request

PERF_RESOURCE_LIST = list(
    os.environ.get("PERF_RESOURCE_LIST") or ["StudentSectionAttendanceEvents"]
)
OAUTH_TOKEN_URL = "/oauth/token/"


class RequestClient:
    """
    The RequestClient class wraps all the configuration complexity related
    to authentication and http requests

    Parameters
    ----------
    api_key : str
        The API client key for EdFi.
    api_secret : str
        The API client secret for EdFi.
    api_base_url : [str]
        The API base url.

    Attributes
    ----------
    oauth : OAuth2Session
        The two-legged authenticated OAuth2 session.
    """

    def __init__(self, args: MainArguments) -> None:
        self.api_base_url = args.baseUrl
        self.page_size = args.pageSize

        self.auth = HTTPBasicAuth(args.key, args.secret)
        client = BackendApplicationClient(client_id=args.key)
        self.oauth = OAuth2Session(client=client)

    def _build_url_for_resource(self, resource) -> str:
        return f"/data/v3/ed-fi/{resource}"

    def _build_query_params_for_page(self, page_index, page_size: int) -> str:
        page_offset = (page_index - 1) * page_size
        return f"offset={page_offset}&limit={page_size}"

    def _build_query_params_for_total_count(self) -> str:
        return f"offset={0}&limit={0}&totalCount=true"

    def _authorize(self) -> None:
        self.oauth.fetch_token(self.api_base_url + OAUTH_TOKEN_URL, auth=self.auth)

    def _get(self, relative_url: str) -> Response:
        """
        Send an HTTP GET request.

        Parameters
        ----------
        relative_url : str
            The resource endpoint that you want to request.

        Returns
        -------
        dict
            A parsed response from the server

        Raises
        -------
        RuntimeError
            If the GET operation is unsuccessful
        """
        assert isinstance(
            self.api_base_url, str
        ), "Property `api_base_url` should be of type `str`."

        if not self.oauth.authorized:
            self._authorize()

        url = self.api_base_url + relative_url

        response: Response

        def _get() -> Response:
            return self.oauth.get(
                url=url,
                auth=self.oauth.auth,
            )

        try:
            response = _get()
        except TokenExpiredError:
            self._authorize()
            response = _get()
            # If that fails after authorization, then let it go

        return response

    def _get_total(self, relative_url: str) -> int:
        response = self._get(relative_url)

        total = response.headers["total-count"]
        return int(total)

    def get_total(self, resource: str = PERF_RESOURCE_LIST[0]) -> int:
        """
        Get total resource count by sending an HTTP GET request.

        Parameters
        ----------
        resource : str
            The resource endpoint that you want to request.

        Returns
        -------
        int
            Total resource count

        Raises
        -------
        RuntimeError
            If the GET operation is unsuccessful
        """

        total_count_url = f"{self._build_url_for_resource(resource)}?{self._build_query_params_for_total_count()}"
        return self._get_total(total_count_url)

    def get_page(
        self,
        resource: str = PERF_RESOURCE_LIST[0],
        page: int = 1,
        page_size: Optional[int] = None,
    ) -> PaginatedResult:
        """Send an HTTP GET request for the next page.

        Returns
        -------
        PaginatedResult
        """

        if page_size is None:
            page_size = self.page_size

        next_url = (
            f"{self._build_url_for_resource(resource)}?"
            f"{self._build_query_params_for_page(page, page_size)}"
        )

        response: Response = self._get(next_url)

        return PaginatedResult(
            resource_name=resource,
            current_page=page,
            page_size=page_size,
            api_response=response.json(),
            status_code=response.status_code,
        )

    def get_all(
        self, resource: str = PERF_RESOURCE_LIST[0], page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Send an HTTP GET request for all pages of a resource.

        Parameters
        ----------
        page_size : int
            Number of items per page

        Returns
        -------
        list
            A list of all parsed results
        """

        if page_size is None:
            page_size = self.page_size

        def _timed_get(page: int) -> PaginatedResult:
            elapsed: float
            response: PaginatedResult
            elapsed, response = Measurement.timeit(
                lambda: self.get_page(resource, page, page_size)
            )

            log_request(
                resource,
                self.api_base_url,
                page,
                page_size,
                len(response.current_page_items),
                elapsed,
                response.status_code,
            )

            return response

        pagination_result = _timed_get(1)

        items: List[Any] = []
        i = 0
        while True:
            items.extend(pagination_result.current_page_items)
            pagination_result = _timed_get(pagination_result.current_page + 1)
            print(i)
            i += 1
            if pagination_result.is_empty:
                break

        return items
