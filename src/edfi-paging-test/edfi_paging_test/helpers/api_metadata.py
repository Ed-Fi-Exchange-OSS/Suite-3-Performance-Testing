# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import requests
import urllib3
from functools import cache
from typing import Any, List, Dict

# Supres insecure request warnings from the console
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


@cache
def get_base_api_response(api_base_url: str, verify_cert: bool = True) -> Dict[str, Any]:
    """
    Gets the metadata response from the base API. Cached to avoid multiple requests.

    Parameters
    ----------
    api_base_url : str
        The base URL of the API.

    Returns
    -------
    Dict
        The API metadata response from the server
    """
    logger.debug("Getting metadata from the api root.")
    try:
        return requests.get(
            api_base_url,
            verify=verify_cert
            ).json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error: {e}.") from e


@cache
def get_openapi_metadata_response(api_base_url: str, verify_cert: bool = True) -> List[Dict[str, str]]:
    """
    Gets the OpenAPI metadata response from the base API. Cached to avoid multiple
    requests.

    Parameters
    ----------
    api_base_url : str
        The base URL of the API.

    Returns
    -------
    Dict
        The OpenAPI metadata response from the server
    """
    logger.debug("Getting OpenAPI metadata from the api.")
    base_api_response: Dict[str, Dict[str, str]] = get_base_api_response(api_base_url, verify_cert)
    return requests.get(
        base_api_response["urls"]["openApiMetadata"],
        verify=verify_cert
        ).json()


@cache
def get_resource_metadata_response(api_base_url: str, verify_cert: bool = True) -> Dict[str, Dict[str, str]]:
    """
    Gets the resource metadata response from the base API. Cached to avoid multiple
    requests.

    Parameters
    ----------
    api_base_url : str
        The base URL of the API.

    Returns
    -------
    Dict
        The resource metadata response from the server
    """
    logger.debug("Getting resource metadata from the api.")
    openapi_metadata: List[Dict[str, str]] = get_openapi_metadata_response(api_base_url, verify_cert)
    resource_metadata: Dict[str, str] = next(
        filter(lambda x: x["name"] == "Resources", openapi_metadata)
    )
    return requests.get(
        resource_metadata["endpointUri"],
        verify=verify_cert
        ).json()


def get_resource_paths(api_base_url: str, verify_cert: bool = True) -> List[str]:
    """
    Gets the resources for the API as relative paths, including the
    project/extension prefix.

    Parameters
    ----------
    api_base_url : str
        The base URL of the API.

    Returns
    -------
    List[str]
        A list of resource relative paths, including the extension prefix if
        relevant. For example: ["schools", "tpdm/candidates"]
    """
    resource_metadata_response: Dict[
        str, Dict[str, str]
    ] = get_resource_metadata_response(api_base_url, verify_cert)
    all_paths: List[str] = list(resource_metadata_response["paths"].keys())
    # filter out paths that are for get by id, deletes, keyChanges or partitions
    return list(
        filter(
            lambda p: (
            "{id}" not in p
            and "/deletes" not in p
            and "/keyChanges" not in p
            and "/partitions" not in p
            )
            , all_paths
        )
    )


def normalize_resource_paths(resource_paths: List[str]) -> List[str]:
    """
    Takes a list of resource relative paths and normalizes to lowercase
    and with the "ed-fi" namespace prefix removed.

    Parameters
    ----------
    resource_paths : List[str]
        The list of resource relative paths

    Returns
    -------
    List[str]
        A list of normalized resource relative paths.
        For example: ["studentschoolassociations", "tpdm/candidates"]
    """
    return list(
        map(
            lambda r: r.removeprefix("/").removeprefix("ed-fi/"),
            resource_paths,
        )
    )
