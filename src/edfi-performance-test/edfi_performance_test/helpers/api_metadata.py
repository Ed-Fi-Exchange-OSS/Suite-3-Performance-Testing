# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import urllib.request


DEFAULT_DATA_STANDARD_VERSION = 3


def get_model_version(baseUrl: str = "") -> int:
    """
    Get the version Number from API dataModels.

    Args:
        baseUrl: String
    Returns:
        Version: String
    """

    with urllib.request.urlopen(baseUrl) as url:
        data = json.load(url)

        for info in data['dataModels']:
            if (info['name'] == 'Ed-Fi'):
                version = int(info['version'][0:1])

    if not version:
        version = int(DEFAULT_DATA_STANDARD_VERSION)

    return version
