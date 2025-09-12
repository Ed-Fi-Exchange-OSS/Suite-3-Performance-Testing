# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import chain, combinations
import logging
import time
from typing import Any, Dict, List, Tuple

from pandas import DataFrame, Series

from edfi_paging_test.api.request_client import RequestClient
from edfi_paging_test.reporter import reporter
from edfi_paging_test.helpers.main_arguments import MainArguments
from edfi_paging_test.helpers.output_format import OutputFormat
from edfi_paging_test.helpers.api_metadata import get_filters_by_resource_name
from edfi_paging_test.reporter.summary import Summary
from edfi_paging_test.helpers.test_type import TestType
from edfi_paging_test.helpers.resource_entries_cache import ResourceEntriesCache

from edfi_paging_test.reporter.paging_request_logger import PaggingRequestLogger
from edfi_paging_test.reporter.filtered_read_request_logger import FilteredReadRequestLogger

logger = logging.getLogger(__name__)


def _generate_output_reports(args: MainArguments, df: DataFrame, statistics: Series) -> None:
    run_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    create_detail_out = {
        OutputFormat.CSV: reporter.create_detail_csv,
        OutputFormat.JSON: reporter.create_detail_json,
    }
    create_detail_out[args.contentType](df, args.output, run_name)

    create_statistics_out = {
        OutputFormat.CSV: reporter.create_statistics_csv,
        OutputFormat.JSON: reporter.create_statistics_json,
    }
    create_statistics_out[args.contentType](statistics, args.output, run_name)
    summary = Summary(
        run_name=run_name, run_configration=args
    )
    reporter.create_summary_json(summary.get_DataFrame(), args.output, run_name)


def fetch_resource_entries(request_client: RequestClient, resource_name: str, pagingRequestLogger: PaggingRequestLogger) -> Tuple[str, List[Dict[str, Any]]]:
    entries = request_client.get_all(resource_name, pagingRequestLogger)
    total_count = request_client.get_total(resource_name)

    if len(entries) != total_count:
        logger.warn(
            f"{resource_name}: expected {total_count} results, got: {len(entries)}"
        )

    return (resource_name, entries)


def fetch_filtered_resources_entries(request_client: RequestClient, resource_name: str, resource: Dict[str, Any], filters: Tuple[str, ...], filteredReadRequestLogger: FilteredReadRequestLogger):
    """
    Retrieves the first 100 entries that match the given filters.
    The filter values are taken from the provided resource entry.
    """

    params = {filter: resource[filter] for filter in filters}
    entries = request_client.filtered_get(resource_name, params, 100, filteredReadRequestLogger)

    if len(entries) == 0:
        logger.warning(
            f'Expected at least 1 entry to be returned while filtering the resource "{resource_name}"')


def invalid_resources(
    openapi_resources: List[str], resources_to_check: List[str]
) -> List[str]:
    return [r for r in resources_to_check if r not in openapi_resources]


def capitalize_first(text):
    return text[0].upper() + text[1:]


def get_filter_combinations(filters: List[str], combination_size_limit):
    """
    Generates combinations of filters.

    Args:
        filters: List of filters that a resource supports
        combination_size_limit: The generated combinations will be of size 1 up to this limit

    Returns:
        List containing different combinations of filters
    """

    return list(chain(*[combinations(filters, i + 1) for i in range(combination_size_limit)]))


async def run(args: MainArguments) -> None:

    try:
        logger.info("Starting paging volume test...")
        start = time.time()
        paggingRequestLogger = PaggingRequestLogger()
        filteredReadRequestLogger = FilteredReadRequestLogger()

        filters_by_resource_name = get_filters_by_resource_name(
            args.baseUrl, not args.ignoreCertificateErrors)

        resource_names: List[str] = list(filters_by_resource_name.keys())
        if len(args.resourceList) == 0:
            args.resourceList = resource_names
        else:
            invalid_env_resources: List[str] = invalid_resources(
                openapi_resources=resource_names,
                resources_to_check=args.resourceList,
            )
            if len(invalid_env_resources) != 0:
                raise RuntimeError(
                    f"Invalid resources found: {','.join(invalid_env_resources)}"
                )

        request_client: RequestClient = RequestClient(args)

        executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=args.connectionLimit
        )
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        fetch_resource_calls: List[asyncio.Future] = [
            loop.run_in_executor(
                executor, fetch_resource_entries, request_client, target_resource, paggingRequestLogger
            )
            for target_resource in args.resourceList
        ]

        completed_fetch_resource_calls, _ = await asyncio.wait(fetch_resource_calls)

        if args.test_type == TestType.FILTERED_READ:
            logger.info("Starting filtered read tests...")

            entries_by_resource_name: Dict[str, List[Dict[str, Any]]] = {
                call.result()[0]: call.result()[1] for call in completed_fetch_resource_calls}

            entries_to_query: List[Tuple[str, Dict[str, Any], Tuple[str, ...]]] = []

            for resource_name, entries in entries_by_resource_name.items():
                if len(entries) == 0:
                    continue

                supported_filters = filters_by_resource_name[resource_name]
                filter_combinations = get_filter_combinations(supported_filters, args.combination_size_limit)

                entriesCache = ResourceEntriesCache(entries, supported_filters)

                for filter_combination in filter_combinations:

                    # Limit to 10 entries per combination (configurable in future versions)
                    entries_with_non_null_filters = entriesCache.get_entries_with_non_null_filters(
                        filter_combination, 10)

                    if len(entries_with_non_null_filters) == 0:
                        continue

                    entries_to_query.extend([(resource_name, entry, filter_combination)
                                            for entry in entries_with_non_null_filters])

            query_resource_calls: List[asyncio.Future] = [
                loop.run_in_executor(
                    executor, fetch_filtered_resources_entries, request_client, resource_name, entry, filter_combination, filteredReadRequestLogger
                )
                for (resource_name, entry, filter_combination) in entries_to_query
            ]

            await asyncio.wait(query_resource_calls)

        dt = paggingRequestLogger.get_DataFrame(
        ) if args.test_type == TestType.DEEP_PAGING else filteredReadRequestLogger.get_DataFrame()
        statistics = paggingRequestLogger.get_statistics(
        ) if args.test_type == TestType.DEEP_PAGING else filteredReadRequestLogger.get_statistics()

        _generate_output_reports(args, dt, statistics)
        logger.info(
            f"Finished with paging volume test in {time.time() - start} seconds."
        )
    except BaseException as err:
        logger.error(err)
