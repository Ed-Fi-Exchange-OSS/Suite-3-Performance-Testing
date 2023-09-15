# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path

from edfi_perf_test_analysis.analysis_helpers import (
    display_exceptions,
    display_failures,
    display_stats,
)
from edfi_perf_test_analysis.ui_helpers import (
    select_directory,
    get_result_directory
)


def run_analysis() -> None:

    results_dir = get_result_directory() [0]
    if results_dir == "":
        results_dir = select_directory()

    display_exceptions(results_dir, "pipeclean")
    display_failures(results_dir, "pipeclean")
    display_stats(results_dir, "pipeclean")
