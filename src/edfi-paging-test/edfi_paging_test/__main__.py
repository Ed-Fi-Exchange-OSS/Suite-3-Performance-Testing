# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dotenv import load_dotenv
from edfi_paging_test.helpers.argparser import parse_main_arguments
from edfi_paging_test.api.request_client import RequestClient


def main() -> None:

    load_dotenv()
    arguments = parse_main_arguments()
    request_client: RequestClient = RequestClient(arguments)

    resources = request_client.get_all()
    total_count = request_client.get_total()

    print(arguments.baseUrl)
    print(arguments.key)
    print(arguments.resourceList)
    print(arguments.pageSize)
    print(f"Resource count: {len(resources)}")
    assert total_count == len(
            resources
    ), f"Expected {total_count} results, got: {len(resources)}"


if __name__ == "__main__":
    main()
