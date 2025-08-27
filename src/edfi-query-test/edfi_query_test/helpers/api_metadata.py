# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import requests
import urllib3
from functools import cache
from typing import Any, List, Dict

from edfi_query_test.helpers.query_param import QueryParam

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


def get_query_params_by_resource(api_base_url: str, verify_cert: bool = True) -> Dict[str, List[QueryParam]]:
    """
    Retrieves query parameters available for each Ed-Fi API resource.
    
    Analyzes the Ed-Fi API's OpenAPI metadata to determine which query parameters
    are available for each resource endpoint, filtering out non-queryable paths.
    
    Args:
        api_base_url (str): Base URL of the Ed-Fi API
        verify_cert (bool): Whether to verify SSL certificates
        
    Returns:
        Dict[str, List[QueryParam]]: Dictionary mapping resource names to their
                                    available query parameters
    """

    resource_metadata_response: Dict[str, Dict[str, Any]
                                     ] = get_resource_metadata_response(api_base_url, verify_cert)

    # filter out paths that are for get by id, deletes, keyChanges or partitions
    operations_by_resource = [(normalize_resource_path(path), operations) for path, operations in resource_metadata_response["paths"].items()
                              if "{id}" not in path
                              and "/deletes" not in path
                              and "/keyChanges" not in path
                              and "/partitions" not in path]

    query_params_by_resource = {resource: get_query_params(
        operations) for resource, operations in operations_by_resource}

    return query_params_by_resource


def get_query_params(operations) -> List[QueryParam]:
    pagination_params = {'limit', 'offset', 'totalCount'}
    return [QueryParam(name=param['name']) for param in operations['get']['parameters'] 
            if 'in' in param and param['in'] == 'query' 
            and param['name'] != 'id'
            and param['name'] not in pagination_params]


def normalize_resource_path(resource_path: str) -> str:
    """
    Takes a list of resource relative paths and normalizes to lowercase
    and with the "ed-fi" namespace prefix removed.

    Parameters
    ----------
    resource_paths : List[str]
        The list of resource relative paths

    Returns
    -------
    str
        A normalized resource relative path.
        For example: "studentschoolassociations", "tpdm/candidates"
    """
    return resource_path.removeprefix("/").removeprefix("ed-fi/")
