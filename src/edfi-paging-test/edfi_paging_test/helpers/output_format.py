# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from enum import Enum


class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"

    @classmethod
    def _missing_(cls, value: str) -> "OutputFormat":
        for member in cls:
            if member.value == value.upper():
                return member

        raise ValueError(f"{value} is not a valid OutputFormat")

    def __str__(self):
        return self.value
