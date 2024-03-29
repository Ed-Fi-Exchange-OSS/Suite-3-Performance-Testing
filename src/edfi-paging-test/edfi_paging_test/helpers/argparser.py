# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from configargparse import ArgParser  # type: ignore

from edfi_paging_test.helpers.output_format import OutputFormat
from edfi_paging_test.helpers.log_level import LogLevel
from edfi_paging_test.helpers.main_arguments import MainArguments


def parse_main_arguments() -> MainArguments:
    """
    Configures the command-line interface.
    Parameters
    ----------
    args_in : list of str
        Full argument list from the command line.
    Returns
    -------
    arguments  : MainArguments
        A populated `MainArguments` object.
    """

    parser = ArgParser()

    parser.add(  # type: ignore
        "-b",
        "--baseUrl",
        help="The base url used to derive the api, metadata, oauth, and dependency urls (e.g., http://server).",
        type=str,
        required=True,
        env_var="PERF_API_BASEURL",
    )
    parser.add(  # type: ignore
        "-k",
        "--key",
        help="The web API OAuth key",
        type=str,
        required=True,
        env_var="PERF_API_KEY",
    )
    parser.add(  # type: ignore
        "-s",
        "--secret",
        help="The web API OAuth secret",
        type=str,
        required=True,
        env_var="PERF_API_SECRET",
    )
    parser.add(  # type: ignore
        "-i",
        "--ignoreCertificateErrors",
        help="Certificate errors are ignored",
        action='store_true',  # default false
        env_var="IGNORE_TLS_CERTIFICATE",
    )
    parser.add(  # type: ignore
        "-c",
        "--connectionLimit",
        help="Maximum concurrent connections to api",
        type=int,
        default=5,
        env_var="PERF_CONNECTION_LIMIT",
    )
    parser.add(  # type: ignore
        "-o",
        "--output",
        help="Directory for writing results",
        type=str,
        default="out",
        env_var="PERF_OUTPUT_DIR",
    )
    parser.add(  # type: ignore
        "-t",
        "--contentType",
        help="CSV or JSON",
        choices=list(OutputFormat),
        default=OutputFormat.CSV,
        type=OutputFormat,
        env_var="PERF_CONTENT_TYPE",
    )
    parser.add(  # type: ignore
        "-r",
        "--resourceList",
        help="(Optional) List of resources to test  - if not provided, all resources will be retrieved",
        nargs="+",
        env_var="PERF_RESOURCE_LIST",
    )
    parser.add(  # type: ignore
        "-p",
        "--pageSize",
        help="The page size to request. Max: 500.",
        type=int,
        default="100",
        env_var="PERF_API_PAGE_SIZE",
    )
    parser.add(  # type: ignore
        "-l",
        "--logLevel",
        help="Console log level: VERBOSE, DEBUG, INFO, WARN, ERROR",
        type=LogLevel,
        choices=list(LogLevel),
        default=LogLevel.INFO,
        env_var="PERF_LOG_LEVEL",
    )
    parser.add(  # type: ignore
        "-d",
        "--description",
        help="Description for the test run",
        type=str,
        default="Paging Volume Test Run",
        env_var="PERF_DESCRIPTION",
    )

    args_parsed = parser.parse_args()

    arguments = MainArguments(
        args_parsed.baseUrl,
        args_parsed.connectionLimit,
        args_parsed.key,
        args_parsed.secret,
        args_parsed.ignoreCertificateErrors,
        args_parsed.output,
        args_parsed.description,
        args_parsed.contentType,
        args_parsed.resourceList or [],
        args_parsed.pageSize,
        args_parsed.logLevel,
    )

    return arguments
