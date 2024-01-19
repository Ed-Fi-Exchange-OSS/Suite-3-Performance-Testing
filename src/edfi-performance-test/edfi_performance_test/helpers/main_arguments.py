# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from typing import List

from edfi_performance_test.helpers.log_level import LogLevel
from edfi_performance_test.helpers.test_type import TestType


@dataclass
class MainArguments:
    """
    Container for holding arguments parsed at the command line.
    """

    baseUrl: str
    key: str
    secret: str
    ignoreCertificateErrors: bool
    testType: TestType
    testList: List[str]
    deleteResources: bool
    failDeliberately: bool
    clientCount: int
    spawnRate: int
    runTimeInMinutes: int
    runInDebugMode: bool
    output: str
    api_prefix: str
    oauth_endpoint: str
    localEducationOrganizationId: int
    log_level: LogLevel = LogLevel.INFO
    disableComposites: bool = False
    includeID: bool = False

    def __str__(self) -> str:
        def _masked(key: str) -> str:
            return getattr(self, key) if key != "secret" else "****"

        return ", ".join([
            f"({key}, {_masked(key)})"
            for key in dir(self)
            if not callable(key) and not key.startswith("__")
        ])
