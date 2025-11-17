# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.helpers.case_insensitive_enum import CaseInsensitiveEnum


class TestType(CaseInsensitiveEnum):
    PIPECLEAN = "pipeclean"
    VOLUME = "volume"
    CHANGE_QUERY = "change_query"
    BATCH_VOLUME = "batch_volume"
