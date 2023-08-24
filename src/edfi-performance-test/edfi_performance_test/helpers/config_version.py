# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import urllib.request


DEFAULT_DATA_STANDARD_VERSION = "3.3.1-b"


def get_config_version(baseUrl: str = "") -> str:
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
                version = info['version']

    if not version:
        version = DEFAULT_DATA_STANDARD_VERSION

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

    with urllib.request.urlopen(url_metadata) as url:
        data = json.load(url)

    metadata = []
    for info in data['tags']:
        metadata.append(info['name'].lower())

    return metadata


def exclude_endpoints_by_version(baseUrl: str, testList: list[str]) -> list[str]:
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

    exceptions = ["disciplines", "accountabilities", "communities", "composites", "descriptors", "educations", "enrollments", "gradebookentries", "postsecondaries", "restraints"]

    for val in testList:
        name = val.replace(val[0:val.rfind(".") + 1], "").replace("_", "").lower()

        if name.endswith("y"):
            name = name[:-1] + "ies"
        else:
            name = name if name.endswith("s") else name + "s"

        if name not in metadata and name not in exceptions:
            # print(name)
            testList.remove(val)

    return testList
