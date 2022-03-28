# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import asyncio
import sys
import logging

from dotenv import load_dotenv
from errorhandler import ErrorHandler

from edfi_paging_test.helpers.argparser import parse_main_arguments
from edfi_paging_test.helpers.main_arguments import MainArguments
from edfi_paging_test.performance_tester import run
from edfi_paging_test.helpers.log_level import LogLevel


def _redefine_debug_as_verbose(configuration: MainArguments, logger: str) -> None:
    requests_logger = logging.getLogger(logger)
    if configuration.log_level == LogLevel.VERBOSE:
        requests_logger.setLevel(logging.DEBUG)
    else:
        requests_logger.setLevel(logging.INFO)


def _configure_logging(configuration: MainArguments) -> None:

    # Verbose is not a real Python log level, so convert back to DEBUG. Verbose
    # is used for quieting other loggers when in DEBUG mode.
    log_level = str(LogLevel.DEBUG if configuration.log_level == LogLevel.VERBOSE else configuration.log_level)

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=log_level,
    )

    # These two loggers produce far more than we really want to see in debug
    # mode. Therefore we'll redefine _their_ debug modes as "verbose" for our
    # purposes.
    _redefine_debug_as_verbose(configuration, "requests_oauthlib.oauth2_session")
    _redefine_debug_as_verbose(configuration, "urllib3.connectionpool")


async def main() -> None:
    load_dotenv()
    configuration = parse_main_arguments()
    _configure_logging(configuration)

    # Important that this comes _after_ the logging configuration
    error_tracker = ErrorHandler()

    await run(configuration)

    if error_tracker.fired:
        print(
            "A fatal error occurred, please review the log output for more information.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
