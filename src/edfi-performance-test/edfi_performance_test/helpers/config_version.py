# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import urllib.request
import ssl
import logging


logger = logging.getLogger()
DEFAULT_API_VERSION = "3.3.1-b"


def get_config_version(baseUrl: str = "") -> str:
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
                version = info['version']

    if not version:
        version = DEFAULT_API_VERSION

    return version


def get_metadata(baseUrl: str = "") -> list[str]:
    """
    Get a list of strings with version endpoints

    Args:
        baseUrl: String

    Returns:
        list[str]
    """
    url_metadata = str(baseUrl) + '/metadata/resources/swagger.json'
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url_metadata, context=context) as url:
        data = json.load(url)

    metadata = []
    for info in data['tags']:
        metadata.append(info['name'].lower())

    return metadata


def exclude_endpoints_by_version(baseUrl: str, testList: list[str], replaceVal: str) -> list[str]:
    """
        Filter the endpoint list searching in the metadata

    Args:
        baseUrl: String
        testList: List of Strings
        replaceVal: String


    Returns:
        list[str]
    """
    metadata = get_metadata(baseUrl)

    for val in testList:
        name = val.replace(replaceVal, "") + "s"
        name = name.replace("_", "").lower()
        exceptions = ["disciplines", "edfivolumetestbases", "volumetestss", "communitys", "composites", "descriptorss", "enrollments", "gradebookentriess", "restraints", "pipecleantestss", "edfipipecleantestbases"]

        if name not in metadata and name not in exceptions:
            testList.remove(val)

    return testList
