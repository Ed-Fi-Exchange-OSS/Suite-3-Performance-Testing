# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_paging_test.helpers.case_insensitive_enum import CaseInsensitiveEnum


class LogLevel(CaseInsensitiveEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    VERBOSE = "VERBOSE"

    def __eq__(self, other: object) -> bool:
        return self.value == LogLevel(other).value
