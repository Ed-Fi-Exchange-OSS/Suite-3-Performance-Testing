# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_paging_test.helpers.case_insensitive_enum import CaseInsensitiveEnum


class TestType(CaseInsensitiveEnum):
    DEEP_PAGING = "DEEP_PAGING"
    FILTERED_READ = "FILTERED_READ"

    def __eq__(self, other: object) -> bool:
        try:
            return self.value == TestType(other).value
        except:  # noqa: E722
            return False

    # Prevent pytest from trying to discover tests in this class
    __test__ = False
