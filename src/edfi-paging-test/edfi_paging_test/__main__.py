# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dotenv import load_dotenv
from edfi_paging_test.helpers.argparser import parse_main_arguments
from edfi_paging_test.api.request_client import RequestClient
from edfi_paging_test.reporter import request_logger
from edfi_paging_test.reporter import reporter


def main() -> None:

    load_dotenv()
    arguments = parse_main_arguments()
    request_client: RequestClient = RequestClient(arguments)

    # TODO: once we are reading multiple requests, we probably want to pass the
    # endpoint to the calls below. I like the call to get_total. The assert
    # should become a WARNING log (see new ticket PERF-233 for logging). we
    # probably want a module that wraps up the calls to get_all(), get_total(),
    # and the validation. Finally, we will want a facade that pulls everything
    # together, so that __main__.py does not need to have any business logic.
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

    df = request_logger.get_DataFrame()
    # Hm, hard-coded run, change to datetime?
    reporter.create_detail_csv(df, arguments.output, "1")
    reporter.create_summary_csv(df, arguments.output, "1")


if __name__ == "__main__":
    main()
