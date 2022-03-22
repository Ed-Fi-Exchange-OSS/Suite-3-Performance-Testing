# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from datetime import datetime
import logging

from edfi_paging_test.api.request_client import RequestClient
from edfi_paging_test.reporter import request_logger
from edfi_paging_test.reporter import reporter
from edfi_paging_test.helpers.argparser import MainArguments
from edfi_paging_test.helpers.output_format import OutputFormat

logger = logging.getLogger(__name__)


def _generate_output_reports(args: MainArguments) -> None:
    df = request_logger.get_DataFrame()

    run_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    create_detail_out = {
        OutputFormat.CSV: reporter.create_detail_csv,
        OutputFormat.JSON: reporter.create_detail_json
    }
    create_detail_out[args.contentType](df, args.output, run_name)

    create_statistics_out = {
        OutputFormat.CSV: reporter.create_statistics_csv,
        OutputFormat.JSON: reporter.create_statistics_json
    }
    create_statistics_out[args.contentType](df, args.output, run_name)


def run(args: MainArguments) -> None:

    try:
        logger.info("Starting paging volume test...")
        request_client: RequestClient = RequestClient(args)

        # TODO: once we are reading multiple requests, we probably want to pass the
        # endpoint to the calls below. I like the call to get_total. The assert
        # should become a WARNING log (see new ticket PERF-233 for logging). we
        # probably want a module that wraps up the calls to get_all(), get_total(),
        # and the validation.
        resources = request_client.get_all()
        total_count = request_client.get_total()

        assert total_count == len(
            resources
        ), f"Expected {total_count} results, got: {len(resources)}"

        _generate_output_reports(args)
        logging.info("Finished with paging volume test.")
    except BaseException as err:
        logger.error(err)
