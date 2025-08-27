# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryParam:
    """
    Represents a query parameter that can be used in Ed-Fi API requests.

    This class encapsulates the information needed to construct query parameters
    for testing different API endpoint combinations and their performance
    characteristics.

    Attributes:
        name (str): The name of the query parameter (e.g., 'studentUniqueId',
                   'schoolId', 'gradingPeriodDescriptor').
    """
    name: str
