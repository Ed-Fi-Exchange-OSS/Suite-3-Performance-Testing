# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


import json
import urllib.request
import ssl

DEFAULT_API_VERSION = "3.3.1-b"


class ConfVersion:
    def get_config_version(self, baseUrl: str = ""):
        """
        Get the version Number from API dataModels.

        Args:
            baseUrl: String
        Returns:
            Version: String
        """

        context = ssl._create_unverified_context()
        with urllib.request.urlopen(baseUrl, context=context) as url:
            data = json.load(url)

            for info in data['dataModels']:
                if (info['name'] == 'Ed-Fi'):
                    return info['version']

        return DEFAULT_API_VERSION
