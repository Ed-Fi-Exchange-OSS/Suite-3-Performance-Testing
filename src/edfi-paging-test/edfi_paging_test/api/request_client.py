# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
import os
from typing import Any, Dict, List
from http import HTTPStatus
import socket

from opnieuw import retry
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import ProtocolError
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session  # type: ignore
from edfi_paging_test.api.paginated_result import PaginatedResult


REQUEST_RETRY_TIMEOUT_SECONDS = 60
PERF_RESOURCE_LIST = list(
    os.environ.get("PERF_RESOURCE_LIST") or ["StudentSectionAttendanceEvents"]
)
OAUTH_TOKEN_URL = "/oauth/token/"


@dataclass
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

    api_key: str = str(os.environ.get("PERF_API_KEY"))
    api_secret: str = str(os.environ.get("PERF_API_SECRET"))
    api_base_url: str = str(os.environ.get("PERF_API_BASEURL"))
    retry_count: int = int(os.environ.get("PERF_RETRY_COUNT") or 4)
    page_size: int = int(os.environ.get("PERF_API_PAGE_SIZE") or 100)

    def __post_init__(self) -> None:
        self.auth = HTTPBasicAuth(self.api_key, self.api_secret)
        client = BackendApplicationClient(client_id=self.api_key)
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

    def _check_response(
        self, response: Response, success_status: HTTPStatus, http_method: str, url: str
    ) -> None:
        """
        Check a response for success

        Parameters
        ----------
        response: Response
            The HTTP response to check
        success_status: HTTPStatus
            The HTTP status that indicates success
        http_method: str
            A human-readable string describing the http method, used for logging
        url: str
            The url of the request, used for logging

        Raises
        -------
        RuntimeError
            If the response indicates failure
        """
        if response.status_code != success_status:
            raise RuntimeError(
                f"{response.reason} ({response.status_code}): {response.text}"
            )

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
        try:
            response = self.oauth.get(
                url=url,
                auth=self.oauth.auth,
            )
        except TokenExpiredError:
            self._authorize()
            raise

        self._check_response(
            response=response, success_status=HTTPStatus.OK, http_method="GET", url=url
        )
        return response

    @retry(
        retry_on_exceptions=(
            IOError,
            TokenExpiredError,
            ConnectionError,
            RequestException,
            HTTPError,
            ProtocolError,
            Timeout,
            RuntimeError,
            socket.timeout,
            socket.error,
        ),
        max_calls_total=retry_count,
        retry_window_after_first_call_in_seconds=REQUEST_RETRY_TIMEOUT_SECONDS,
    )
    def _get_data(self, relative_url: str) -> Dict[str, Any]:
        response = self._get(relative_url)
        return response.json()

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

    def get_page(self, page: int = 1, resource: str = PERF_RESOURCE_LIST[0], page_size: int = page_size) -> PaginatedResult:
        """Send an HTTP GET request for the next page.

        Returns
        -------
        PaginatedResult
        """

        next_url = (
            f"{self._build_url_for_resource(resource)}?"
            f"{self._build_query_params_for_page(page, page_size)}"
        )

        return PaginatedResult(
            resource_name=resource,
            current_page=page,
            page_size=page_size,
            api_response=self._get_data(next_url)
        )

    def get_all(
        self, resource: str = PERF_RESOURCE_LIST[0], page_size: int = page_size
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

        pagination_result = self.get_page()

        items: List[Any] = []
        while True:
            items = items + list(pagination_result.current_page_items)
            pagination_result = self.get_page(pagination_result.current_page + 1)
            if(pagination_result.is_empty):
                break

        return items
