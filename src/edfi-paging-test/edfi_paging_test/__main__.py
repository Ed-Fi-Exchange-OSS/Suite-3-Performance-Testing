# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dotenv import load_dotenv
from edfi_paging_test.helpers.argparser import parse_main_arguments
from edfi_paging_test.performance_tester import run


def main() -> None:

    load_dotenv()
    run(parse_main_arguments())


if __name__ == "__main__":
    main()
