# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import random
from typing import Any, Dict, List, Tuple


class ResourceEntriesCache:

    def __init__(self, entries: List[Dict[str, Any]], filters: List[str]):
        """
        Stores the given resource entries in a columnar fashion to speed up local searches.

        Args:
            entries: Resource entries
            filters: List of filters that a resource supports
        """

        # Create a dictionary where the key is the filter name and the value is a list of entries
        # with a non-null value for the given filter
        self.resources_by_filter_name: Dict[str, list[Dict[str, Any]]] = {filter: [] for filter in filters}

        for entry in entries:
            for filter in filters:
                if filter in entry and entry[filter] is not None:
                    self.resources_by_filter_name[filter].append(entry)

    def get_entries_with_non_null_filters(self, filters: Tuple[str, ...], count: int) -> List[Dict[str, Any]]:
        """
        Searches through the resource entries to find the ones that have non-null values
        for all the specified filters, up to the requested count.

        Args:
            filters: The required filters
            count: Maximum number of matching entries to return
        """

        # Get the filter with the highest cardinality
        entries = list(self.resources_by_filter_name.items())[0][1]
        for filter in filters:
            if len(self.resources_by_filter_name[filter]) < len(entries):
                entries = self.resources_by_filter_name[filter]

        random.shuffle(entries)

        result: List[Dict[str, Any]] = []
        for entry in entries:
            has_all_non_null_filters = True
            for filter in filters:
                if filter not in entry or entry[filter] is None:
                    has_all_non_null_filters = False
                    break

            if has_all_non_null_filters:
                result.append(entry)

            if len(result) >= count:
                break

        return result
