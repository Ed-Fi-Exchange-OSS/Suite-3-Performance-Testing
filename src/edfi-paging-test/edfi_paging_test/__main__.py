# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dotenv import load_dotenv
from helpers.argparser import parse_main_arguments  # type: ignore


def main() -> None:

    load_dotenv()
    arguments = parse_main_arguments()
    print(arguments.baseUrl)
    print(arguments.key)
    print(arguments.resourceList)
    print(arguments.pageSize)


if __name__ == "__main__":
    main()
