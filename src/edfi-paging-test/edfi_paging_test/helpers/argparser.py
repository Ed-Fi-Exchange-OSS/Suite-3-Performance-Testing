# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from configargparse import ArgParser  # type: ignore
from typing import List
from dataclasses import dataclass


@dataclass
class MainArguments:
    """
    Container for holding arguments parsed at the command line.
    """

    baseUrl: str
    connectionLimit: int
    key: str
    secret: str
    output: str
    contentType: str
    retries: str
    resourceList: List[str]
    pageSize: int = 100


def parse_main_arguments(args_in: List[str]) -> MainArguments:
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
    )
    parser.add(  # type: ignore
        "-k",
        "--key",
        help="The web API OAuth key",
        type=str,
        required=True,
    )
    parser.add(  # type: ignore
        "-s",
        "--secret",
        help="The web API OAuth secret",
        type=str,
        required=True,
    )
    parser.add(  # type: ignore
        "-c",
        "--connectionLimit",
        help="Maximum concurrent connections to api",
        type=int,
        default=4,
    )
    parser.add(  # type: ignore
        "-o",
        "--output",
        help="Directory for writing results",
        type=str,
        default="out",
    )
    parser.add(  # type: ignore
        "-t",
        "--contentType",
        help="CSV or JSON",
        type=str,
        default="csv",
    )
    parser.add(  # type: ignore
        "-r",
        "--retries",
        help="Number of time to retry in case of error",
        type=int,
        default=5,
    )
    parser.add(  # type: ignore
        "-l",
        "--resourceList",
        help="(Optional) List of resources to test  - if not provided, all resources will be retrieved",
        nargs='+'
    )
    parser.add(  # type: ignore
        "-p",
        "--pageSize",
        help="The page size to request. Max: 500.",
        type=int,
        default="100",
    )

    args_parsed = parser.parse_args(args_in)

    arguments = MainArguments(
        args_parsed.baseUrl,
        args_parsed.connectionLimit,
        args_parsed.key,
        args_parsed.secret,
        args_parsed.output,
        args_parsed.contentType,
        args_parsed.retries,
        args_parsed.resourceList,
        args_parsed.pageSize
    )

    return arguments
