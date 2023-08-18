# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path
from typing import Tuple

import pandas as pd
import scipy

from edfi_perf_test_analysis.plotting import prepare_for_charts, regression_plot
from edfi_perf_test_analysis.analysis_helpers import (
    display_exceptions,
    display_failures,
    display_stats,
    get_and_prep_stats,
    get_summary_stats,
)
from edfi_perf_test_analysis.ui_helpers import (
    display_df,
    select_directory,
    get_result_directory,
    log_warning,
    markdown,
)


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


def run_analysis() -> Tuple[str, pd.DataFrame]:
    results_dir = get_result_directory() [0]
    if results_dir == "":
        results_dir = select_directory()
    test_type = "volume"

    display_exceptions(results_dir, test_type)
    display_failures(results_dir, test_type)
    df_stats = display_stats(results_dir, test_type)

    prepare_for_charts()

    _display_server_counters(results_dir, test_type, "web")
    _display_server_counters(results_dir, test_type, "db")

    return (results_dir, df_stats)


def run_comparison(left_dir: str, df_left: pd.DataFrame) -> None:

    right_dir = get_result_directory() [1]
    if right_dir == "":
        right_dir = select_directory()

    df_right = get_and_prep_stats(right_dir, "volume")

    markdown("## Summary Statistics")

    markdown("### Left Summary")
    markdown(f"Directory: {left_dir}")
    display_df(get_summary_stats(df_left))

    markdown("### Right Summary")
    markdown(f"Directory: {right_dir}")
    display_df(get_summary_stats(df_right))

    markdown("## Direct Comparison")
    markdown(
        "Hypothesis: the average response times for each request are the same in both sets."
    )

    merged = df_left.merge(df_right, on=["Request"], suffixes=("_l", "_r"))

    mean = "Avg Response Time"
    stdev = "Approx Std Dev"
    count = "Request Count"

    merged["diff"] = merged[f"{mean}_l"] - merged[f"{mean}_r"]

    # Perform a Welch's T-Test using the statistics from the CSV files
    # https://en.wikipedia.org/wiki/Welch%27s_t-test
    # Should only perform T-Test on samples of 30 or more (Central Limit Theorem)
    large_enough = merged[
        (merged[f"{count}_l"] >= 30) & (merged[f"{count}_l"] >= 30)
    ].copy()
    too_few = merged[(merged[f"{count}_l"] < 30) | (merged[f"{count}_l"] < 30)].copy()
    # force garbage collection
    merged = None

    _, p_value = scipy.stats.ttest_ind_from_stats(
        mean1=large_enough[f"{mean}_l"],
        mean2=large_enough[f"{mean}_r"],
        std1=large_enough[f"{stdev}_l"],
        std2=large_enough[f"{stdev}_r"],
        nobs1=large_enough[f"{count}_l"],
        nobs2=large_enough[f"{count}_r"],
        equal_var=False,
    )
    large_enough.loc[:, "T p-value"] = p_value

    markdown("### Worse")
    markdown(
        "95% confident that the response times are in fact different from on another, "
        "and the second data set is worse than the first data set."
    )

    worse = large_enough[
        (large_enough["T p-value"] < 0.05) & (large_enough["diff"] < 0)
    ]
    display_df(worse)

    markdown("### Same")
    markdown("95% confident that the response times are the same.")

    worse = large_enough[(large_enough["T p-value"] >= 0.05)]
    display_df(worse)

    markdown("### Better")
    markdown(
        "95% confident that the response times are in fact different from on another, "
        "and the second data set is better than the first data set."
    )

    better = large_enough[
        (large_enough["T p-value"] < 0.05) & (large_enough["diff"] > 0)
    ]
    display_df(better)

    markdown("### Too Few Data Points")
    markdown(
        "There were < 30 data points for the following, therefore could not perform a "
        "T-Test to statistically compare the distributions."
    )
    display_df(too_few)
