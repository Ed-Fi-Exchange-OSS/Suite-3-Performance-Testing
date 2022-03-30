# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
from typing import Any, Callable, Dict, List, Tuple, TypeVar, Optional
from timeit import default_timer

from requests import Response, adapters
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from oauthlib.oauth2 import TokenExpiredError
from requests_oauthlib import OAuth2Session  # type: ignore

from edfi_paging_test.api.paginated_result import PaginatedResult
from edfi_paging_test.api.api_info import APIInfo
from edfi_paging_test.helpers.argparser import MainArguments
from edfi_paging_test.reporter.request_logger import log_request
from edfi_paging_test.helpers.api_metadata import get_base_api_response

EDFI_DATA_MODEL_NAME = "ed-fi"

T = TypeVar("T")

logger = logging.getLogger(__name__)


def timeit(callback: Callable[[], T]) -> Tuple[float, T]:
    start = default_timer()
    response = callback()
    elapsed = default_timer() - start

    return (elapsed, response)


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
        self.api_info : Optional[APIInfo] = None
        # configure connection pool
        requests_adapter = adapters.HTTPAdapter(
            pool_connections=args.connectionLimit, pool_maxsize=args.connectionLimit
        )
        self.oauth.mount("http://", requests_adapter)
        self.oauth.mount("https://", requests_adapter)

    def _build_url_for_resource(self, resource: str) -> str:
        endpoint = resource
        if "/" not in resource:
            endpoint = EDFI_DATA_MODEL_NAME + "/" + resource

        return f"/data/v3/{endpoint}"

    def _build_query_params_for_page(self, page_index, page_size: int) -> str:
        page_offset = (page_index - 1) * page_size
        return f"offset={page_offset}&limit={page_size}"

    def _get_api_info(self) -> APIInfo:
        """Send an HTTP GET request for the api root to fetch api metadata.

        Returns
        -------
        APIInfo
        """
        if self.api_info is None:
            response = get_base_api_response(self.api_base_url)
            self.api_info = APIInfo(
                version=response["version"],
                api_mode=response["apiMode"],
                datamodels=response["dataModels"],
                urls=response["urls"]
            )
        return self.api_info

    def _authorize(self) -> None:
        logger.debug("Authenticating to the ODS/API")
        self.oauth.fetch_token(self._get_api_info().oauth_url, auth=self.auth)

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

        def __get() -> Response:
            return self.oauth.get(
                url=url,
                auth=self.oauth.auth,
            )

        try:
            response = __get()
        except TokenExpiredError:
            self._authorize()
            response = __get()
            # If that fails after authorization, then let it go

        return response

    def get_total(self, resource: str) -> int:
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
        logger.info(f"Getting total count for {resource}.")
        total_count_url = (
            f"{self._build_url_for_resource(resource)}?offset=0&limit=0&totalCount=true"
        )

        logger.debug(f"GET {total_count_url}")

        response = self._get(total_count_url)

        return int(response.headers["total-count"])

    def get_page(self, resource: str, page: int = 1) -> PaginatedResult:
        """Send an HTTP GET request for the next page.

        Returns
        -------
        PaginatedResult
        """

        next_url = (
            f"{self._build_url_for_resource(resource)}?"
            f"{self._build_query_params_for_page(page, self.page_size)}"
        )

        logger.debug(f"GET {next_url}")
        elapsed, response = timeit(lambda: self._get(next_url))

        items = response.json() if len(response.text) > 0 else []

        log_request(
            resource,
            next_url,
            page,
            self.page_size,
            len(items),
            elapsed,
            response.status_code,
        )

        return PaginatedResult(
            resource_name=resource,
            current_page=page,
            page_size=self.page_size,
            api_response=items,
            status_code=response.status_code,
        )

    def get_all(self, resource: str) -> List[Dict[str, Any]]:
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

        logger.info(f"Retrieving all {resource} records...")

        pagination_result = self.get_page(resource, 1)
        items: List[Any] = pagination_result.current_page_items

        while True:
            pagination_result = self.get_page(
                resource, pagination_result.current_page + 1
            )
            items.extend(pagination_result.current_page_items)

            if pagination_result.size < self.page_size:
                break

        return items
