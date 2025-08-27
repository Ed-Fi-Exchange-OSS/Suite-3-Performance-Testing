# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from itertools import chain, combinations
import logging
import random
import time
from typing import Any, Dict, List, Tuple

from edfi_query_test.api.request_client import RequestClient
from edfi_query_test.reporter import request_logger
from edfi_query_test.reporter import reporter
from edfi_query_test.helpers.main_arguments import MainArguments
from edfi_query_test.helpers.output_format import OutputFormat
from edfi_query_test.helpers.api_metadata import get_query_params_by_resource
from edfi_query_test.reporter.summary import Summary
from edfi_query_test.helpers.query_param import QueryParam


logger = logging.getLogger(__name__)


def _generate_output_reports(args: MainArguments) -> None:
    df = request_logger.get_DataFrame()

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
    create_statistics_out[args.contentType](df, args.output, run_name)
    summary = Summary(
        run_name=run_name, run_configration=args
    )
    reporter.create_summary_json(
        summary.get_DataFrame(), args.output, run_name)


def fetch_resource(request_client: RequestClient, resource_name: str) -> Tuple[str, List[Dict[str, Any]]]:
    resources = request_client.get_all(resource_name)
    total_count = request_client.get_total(resource_name)

    if len(resources) != total_count:
        logger.warn(
            f"{resource_name}: expected {total_count} results, got: {len(resources)}"
        )

    return (resource_name, resources)


def fetch_resource_by_query(request_client: RequestClient, resource_name: str, resource: Dict[str, Any], query_params: Tuple[QueryParam, ...]):

    params = {query_param.name: resource[query_param.name]
              for query_param in query_params}
    entries = request_client.query(resource_name, params)

    if len(entries) == 0:
        logger.warning(
            f'Expected at least 1 record while querying "{resource_name}"')


def invalid_resources(
    openapi_resources: List[str], resources_to_check: List[str]
) -> List[str]:
    return [r for r in resources_to_check if r not in openapi_resources]

# TODO AXEL document
def find_resource_with_all_query_params(resources: List[Dict[str, Any]], query_params: Tuple[QueryParam, ...], count: int) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for resource in resources:
        resource_has_all_query_params = True
        for query_param in query_params:
            if query_param.name not in resource or resource[query_param.name] == None:
                resource_has_all_query_params = False
                break

        if resource_has_all_query_params:
            result.append(resource)

        if len(result) >= count:
            break

    return result


def capitalize_first(text):
    return text[0].upper() + text[1:]


def flatten_resource(resource: Dict[str, Any]) -> Dict[str, Any]:
    # TODO AXEL Doesn't improve matching for DMS because its OpenApi metada is missing nested queryable fields
    flattened = {}

    for key, value in resource.items():
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                flatten_key = key.removesuffix("Reference")
                flatten_key = nested_key if nested_key.lower().startswith(
                    flatten_key.lower()) else flatten_key + capitalize_first(nested_key)
                flattened[flatten_key] = nested_value
        else:
            flattened[key] = value

    return flattened


def get_query_params_combinations(query_params: List[QueryParam]):
    # TODO AXEL make configurable
    return list(chain(*[combinations(query_params, i + 1) for i in range(6)]))


async def run(args: MainArguments) -> None:

    try:
        logger.info("Starting query volume test...")
        start = time.time()

        query_params_by_resource = get_query_params_by_resource(
            args.baseUrl, not args.ignoreCertificateErrors)

        resource_names: List[str] = list(query_params_by_resource.keys())
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
                executor, fetch_resource, request_client, target_resource
            )
            for target_resource in args.resourceList
        ]

        completed_fetch_resource_calls, _ = await asyncio.wait(fetch_resource_calls)
        resources_by_resource_name: Dict[str, List[Dict[str, Any]]] = {
            call.result()[0]: call.result()[1] for call in completed_fetch_resource_calls}

        resources_to_query: List[Tuple[str,
                                       Dict[str, Any], Tuple[QueryParam, ...]]] = []

        for resource_name, resources in resources_by_resource_name.items():
            if len(resources) == 0:
                continue

            query_params = query_params_by_resource[resource_name]
            query_params_combinations = get_query_params_combinations(
                query_params)

            # TODO AXEL document
            resources_by_query_param: dict[str, list[Dict[str, Any]]] = {
                query_param.name: [] for query_param in query_params}
            for resources_with_all_query_params in resources:
                for query_param in query_params:
                    if query_param.name in resources_with_all_query_params and resources_with_all_query_params[query_param.name] != None:
                        resources_by_query_param[query_param.name].append(
                            resources_with_all_query_params)

            for query_params in query_params_combinations:

                # TODO AXEL document
                min_resources = list(resources_by_query_param.items())[0][1]
                for query_param in query_params:
                    if len(resources_by_query_param[query_param.name]) < len(min_resources):
                        min_resources = resources_by_query_param[query_param.name]

                random.shuffle(min_resources)
                # TODO AXEL make configurable
                resources_with_all_query_params = find_resource_with_all_query_params(
                    min_resources, query_params, 10)

                if len(resources_with_all_query_params) == 0:
                    continue

                resources_to_query.extend([(resource_name, resource, query_params)
                                          for resource in resources_with_all_query_params])

        query_resource_calls: List[asyncio.Future] = [
            loop.run_in_executor(
                executor, fetch_resource_by_query, request_client, resource_name, resource, query_params
            )
            for (resource_name, resource, query_params) in resources_to_query
        ]

        await asyncio.wait(query_resource_calls)

        _generate_output_reports(args)
        logger.info(
            f"Finished with query volume test in {time.time() - start} seconds."
        )
    except BaseException as err:
        logger.error(err)
