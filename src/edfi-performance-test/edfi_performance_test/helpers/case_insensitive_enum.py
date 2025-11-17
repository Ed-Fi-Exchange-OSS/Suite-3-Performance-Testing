# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from enum import Enum
from typing import Optional


class CaseInsensitiveEnum(Enum):
    @classmethod
    def _missing_(cls, value: object) -> Optional["CaseInsensitiveEnum"]:
        value_str = str(value)
        for member in cls:
            # Match either on member name (e.g. "BATCH_VOLUME") or on the
            # stored value (e.g. "batch_volume"), in a case-insensitive way.
            if (
                member.name.upper() == value_str.upper()
                or str(member.value).upper() == value_str.upper()
            ):
                return member

        return None

    def __str__(self):
        return self.value
