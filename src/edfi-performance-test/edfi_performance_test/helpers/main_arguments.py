# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass

from edfi_performance_test.helpers.log_level import LogLevel


@dataclass
class MainArguments:
    """
    Container for holding arguments parsed at the command line.
    """

    baseUrl: str
    key: str
    secret: str
    ignoreCertificateErrors: bool
    deleteResources: bool
    failDeliberately: bool
    clientCount: int
    spawnRate: int
    runTimeInMinutes: int
    runInDebugMode: bool
    output: str
    api_prefix: str
    oauth_endpoint: str
    log_level: LogLevel = LogLevel.INFO
