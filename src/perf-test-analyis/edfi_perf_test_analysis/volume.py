# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path

import pandas as pd

from edfi_perf_test_analysis.plotting import prepare_for_charts, regression_plot
from edfi_perf_test_analysis.analysis_helpers import (
    display_exceptions,
    display_failures,
    display_stats,
)
from edfi_perf_test_analysis.ui_helpers import select_directory, log_warning, markdown


# server stats columns = [
#     "Time",
#     "CPU Load (%)",
#     "Memory Used (%)",
#     "Drive A: Free Space (GB)",
#     "Drive C: Free Space (GB)",
#     "Drive D: Free Space (GB)",
#     "Drive F: Free Space (GB)",
#     "Bytes Received per second",
#     "Bytes Sent per second",
#     "Requests Queued",
#     "Full Scans per second",
#     "Batch Requests per second",
#     "User Connections",
#     "Network IO Waits started per second",
#     "Page IO Latch Waits started per second",
# ]


def _display_server_counters(results_dir: str, test_type: str, server: str) -> None:
    markdown(f"### {server.capitalize()} Server Data")
    file_path = path.join(results_dir, f"{test_type}.ods-3-perf-{server}.csv")
    if not path.exists(file_path):
        log_warning("No data file available for display")
        return

    web = pd.read_csv(file_path)
    # For regression analysis, need to compare numbers to numbers, not numbers
    # to dates. Thus "Time" is not appropriate on the x-axis. Copy the index to
    # a sequence number that can be used instead.
    web["SequenceNumber"] = web.index

    web = web.astype({"CPU Load (%)": "float64", "Memory Used (%)": "float64"})
    regression_plot(web, x="SequenceNumber", y="CPU Load (%)")
    regression_plot(web, x="SequenceNumber", y="Memory Used (%)")


def run_analysis() -> None:

    results_dir = select_directory()

    test_type = "volume"

    display_exceptions(results_dir, test_type)
    display_failures(results_dir, test_type)
    display_stats(results_dir, test_type)

    prepare_for_charts()

    _display_server_counters(results_dir, test_type, "web")
    _display_server_counters(results_dir, test_type, "db")
