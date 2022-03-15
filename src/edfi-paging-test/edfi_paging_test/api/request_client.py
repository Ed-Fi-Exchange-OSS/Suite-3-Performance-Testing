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
from oauthlib.oauth2 import BackendApplicationClient  # type: ignore
from oauthlib.oauth2 import TokenExpiredError  # type: ignore
from requests_oauthlib import OAuth2Session  # type: ignore
from edfi_paging_test.api.paginated_result import PaginatedResult


REQUEST_RETRY_TIMEOUT_SECONDS = 60
PERF_RESOURCE_LIST = list(
    os.environ.get("PERF_RESOURCE_LIST") or ["StudentSectionAttendanceEvents"])
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

    def get(self, resource: str) -> Dict[str, Any]:
        """
        Send an HTTP GET request.
        Parameters
        ----------
        resource : str
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

        if(not self.oauth.authorized):
            self._authorize()

        url = self.api_base_url + resource
        try:
            response = self.oauth.get(
                url=url,
                auth=self.oauth.auth,
                )
        except TokenExpiredError:
            self._authorize()
            raise

        self._check_response(
            response=response, success_status=response.status_code, http_method="GET", url=url
        )
        return response.json()  # type: ignore

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
            socket.error
        ),
        max_calls_total=retry_count,
        retry_window_after_first_call_in_seconds=REQUEST_RETRY_TIMEOUT_SECONDS,
    )
    def get_total(self, resource: str) -> int:
        """
        Send an HTTP GET request.
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
        assert isinstance(
            self.api_base_url, str
        ), "Property `api_base_url` should be of type `str`."

        if(not self.oauth.authorized):
            self._authorize()

        url = self.api_base_url + resource
        try:
            response = self.oauth.get(
                url=url,
                auth=self.oauth.auth,
                )
        except TokenExpiredError:
            self._authorize()
            raise

        self._check_response(
            response=response, success_status=response.status_code, http_method="GET", url=url
        )
        total = response.headers["total-count"]  # type: ignore
        return int(total)

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
            socket.error
        ),
        max_calls_total=retry_count,
        retry_window_after_first_call_in_seconds=REQUEST_RETRY_TIMEOUT_SECONDS,
    )
    def build_url_for_resource(self, resource) -> str:
        return f"/data/v3/ed-fi/{resource}"

    def build_query_params_for_page(self, page_index, page_size: int) -> str:
        page_offset = (page_index - 1) * page_size
        return f"offset={page_offset}&limit={page_size}"

    def build_query_params_for_total_count(self) -> str:
        return f"offset={0}&limit={0}&totalCount=true"

    def get_all(self, resource: str = PERF_RESOURCE_LIST[0], page_size: int = page_size) -> List[Dict[str, Any]]:
        """
        Parameters
        ----------
        page_size : int
            Number of items per page
        Returns
        -------
        PaginatedResult
            A paged response from the API
        """
        url = f"{self.build_url_for_resource(resource)}?{self.build_query_params_for_page(1, page_size)}"
        total_count_url = f"{self.build_url_for_resource(resource)}?{self.build_query_params_for_total_count()}"
        pagination_result = PaginatedResult(
            self,
            page_size=page_size,
            total_count=self.get_total(total_count_url),
            api_response=self.get(url),
            resource_name=PERF_RESOURCE_LIST[0],
        )

        result = pagination_result.get_all_pages()
        assert pagination_result.total_count == len(result), f"Expected {pagination_result.total_count} results, got: {len(result)}"
        return result
