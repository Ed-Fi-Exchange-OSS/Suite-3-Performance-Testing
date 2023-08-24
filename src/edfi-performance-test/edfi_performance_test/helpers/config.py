# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


import os
import json
from edfi_performance_test.helpers.main_arguments import MainArguments
from edfi_performance_test.helpers.config_version import (
    get_config_version,
)


DEFAULT_API_PREFIX = "/data/v3/ed-fi"
DEFAULT_OAUTH_ENDPOINT = "/oauth/token"
DEFAULT_LEA_ID = 255901
DEFAULT_DATA_STANDARD_VERSION = "3.3.1-b"


def get_config_value(key: str, default: str = "") -> str:
    if key in os.environ:
        return os.environ[key]

    if key == "newest_change_version":
        change_version_file = _get_change_version_file_path()
        with open(change_version_file, "r") as version_file:
            os.environ[key] = str(
                json.loads(version_file.read())[key]
            )  # set environment variable to avoid reading the file for each endpoint
            return os.environ[key]

    if default != "":
        return default

    raise RuntimeError(f"Missing environment variable `{key}`")


def set_config_values(args: MainArguments):
    # Although we parse arguments from the command line elsewhere, we go back
    # and inject these into environment variables to make it easy to access them
    # from anywhere in the code, without having to pass the `args` variable
    # around.
    os.environ["PERF_API_KEY"] = args.key
    os.environ["PERF_API_BASEURL"] = args.baseUrl
    os.environ["PERF_DELETE_RESOURCES"] = str(args.deleteResources)
    os.environ["PERF_FAIL_DELIBERATELY"] = str(args.failDeliberately)
    os.environ["IGNORE_TLS_CERTIFICATE"] = str(args.ignoreCertificateErrors)
    os.environ["PERF_API_SECRET"] = args.secret
    os.environ["PERF_API_PREFIX"] = args.api_prefix
    os.environ["PERF_API_OAUTH_PREFIX"] = args.oauth_endpoint
    os.environ["PERF_LOCAL_EDUCATION_ORGANIZATION_ID"] = str(args.localEducationOrganizationId)
    os.environ["PERF_DISABLE_COMPOSITES"] = str(args.disableComposites)
    # PERF-287
    os.environ["PERF_DATA_STANDARD_VERSION"] = get_config_version(str(args.baseUrl))


def _get_change_version_file_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(current_dir, "..")
    current_dir = os.path.join(current_dir, "..")
    change_version_file_path = os.path.join(current_dir, "change_version_tracker.json")
    if not os.path.isfile(change_version_file_path):
        with open(change_version_file_path, "w") as change_version_file:
            change_version_file.write('{\n    "newest_change_version": 0\n}')
    return change_version_file_path


def set_change_version_value(value):
    with open(_get_change_version_file_path(), "w") as change_version_file:
        change_version_file.write(
            json.dumps(
                {"newest_change_version": value}, indent=4, separators=(",", ": ")
            )
        )
