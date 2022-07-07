# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from configargparse import ArgParser  # type: ignore

from edfi_performance_test.helpers.log_level import LogLevel
from edfi_performance_test.helpers.main_arguments import MainArguments


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
        "-d",
        "--deleteResources",
        help="Delete resources during test run",
        action='store_true',  # default false
        env_var="PERF_DELETE_RESOURCES",
    )
    parser.add(  # type: ignore
        "-f",
        "--failDeliberately",
        help="Deliberately introduce requests that result in failure",
        action='store_true',  # default false
        env_var="PERF_FAIL_DELIBERATELY",
    )
    parser.add(  # type: ignore
        "-c",
        "--clientCount",
        help="Total number of users spawned by locust tests",
        type=int,
        default=1000,  # default false
        env_var="CLIENT_COUNT",
    )
    parser.add(  # type: ignore
        "-r",
        "--spawnRate",
        help="Number of users spawned by locust tests per second",
        type=int,
        default=25,  # default false
        env_var="SPAWN_RATE",
    )
    parser.add(  # type: ignore
        "-t",
        "--runTimeInMinutes",
        help="Test Run Time",
        type=int,
        default=30,  # default false
        env_var="RUN_TIME_IN_MINUTES",
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
        "-l",
        "--logLevel",
        help="Console log level: VERBOSE, DEBUG, INFO, WARN, ERROR",
        type=LogLevel,
        choices=list(LogLevel),
        default=LogLevel.INFO,
        env_var="PERF_LOG_LEVEL",
    )
    args_parsed = parser.parse_args()

    arguments = MainArguments(
        args_parsed.baseUrl,
        args_parsed.key,
        args_parsed.secret,
        args_parsed.ignoreCertificateErrors,
        args_parsed.deleteResources,
        args_parsed.failDeliberately,
        args_parsed.clientCount,
        args_parsed.spawnRate,
        args_parsed.runTimeInMinutes,
        args_parsed.output,
        args_parsed.logLevel,
    )

    return arguments
