# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import sys
import logging

from dotenv import load_dotenv
from errorhandler import ErrorHandler

from edfi_paging_test.helpers.argparser import parse_main_arguments
from edfi_paging_test.performance_tester import run


def main() -> None:
    load_dotenv()
    configuration = parse_main_arguments()

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=str(configuration.log_level),
    )

    # Important that this comes _after_ the logging configuration
    error_tracker = ErrorHandler()
    run(configuration)

    if error_tracker.fired:
        print(
            "A fatal error occurred, please review the log output for more information.",
            file=sys.stderr,
        )
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
