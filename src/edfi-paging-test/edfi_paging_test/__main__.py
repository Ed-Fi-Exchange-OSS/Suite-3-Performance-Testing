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
    request_client: RequestClient = RequestClient(
        api_base_url=arguments.baseUrl, api_key=arguments.key, api_secret=arguments.secret, retry_count=arguments.retries, page_size=arguments.pageSize
    )
    resources = request_client.get_all()

    print(arguments.baseUrl)
    print(arguments.key)
    print(arguments.resourceList)
    print(arguments.pageSize)
    print(f"Resource count: {len(resources)}")


if __name__ == "__main__":
    main()
