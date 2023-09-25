# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

DEFAULT_DATA_STANDARD_VERSION = 3


def get_model_version(baseUrl: str = "") -> int:
    """
    Get the version Number from API dataModels.

    Args:
        baseUrl: String
    Returns:
        Version: String
    """

    with urlopen(baseUrl) as url:
        data = json.load(url)

        for info in data['dataModels']:
            if (info['name'] == 'Ed-Fi'):
                version = int(info['version'][0:1])

    if not version:
        version = int(DEFAULT_DATA_STANDARD_VERSION)

    return version


def valid_url(api_base_url: str) -> str:
    """
    Validate the URL accessibility.

    Parameters:
        api_base_url: String

    Returns:
        Boolean:
            True: when accessible.
            False: when an error occurs.
    """
    error = ""
    try:
        urlopen(api_base_url)
    except HTTPError as e:
        # Return code error (e.g. 404, 501, ...)
        error = f'HTTPError: {e.code}'
    except URLError as e:
        # Not an HTTP-specific error (e.g. connection refused)
        error = f'URLError: {e.reason}'
    except TimeoutError:
        error = 'Request time out'

    return error
