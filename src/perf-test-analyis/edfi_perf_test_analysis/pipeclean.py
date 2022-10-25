# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path

import pandas as pd
from edfi_perf_test_analysis.ui_helpers import markdown, display_df, select_directory


def _display_exceptions(results_dir: str) -> None:
    exceptions = pd.read_csv(path.join(results_dir, "pipeclean_exceptions.csv"))
    exceptions.set_index("Message", inplace=True)

    markdown("### Exceptions")
    markdown("First five exceptions")
    display_df(exceptions, 5)


def _display_failures(results_dir: str) -> None:
    failures = pd.read_csv(path.join(results_dir, "pipeclean_failures.csv"))
    failures.set_index("Name", inplace=True)

    markdown("### Failures")
    markdown("First five failures")
    display_df(failures, 5)


def _display_stats(results_dir: str) -> None:
    stats = pd.read_csv(path.join(results_dir, "pipeclean_stats.csv"))

    # Remove the "Aggregated" row
    stats.drop(stats.index[stats["Name"] == "Aggregated"], inplace=True)

    # Create a new column combining Type and Name, then index on it
    stats["Request"] = stats["Type"] + " " + stats["Name"]
    stats.set_index("Request", inplace=True)

    stats = stats[["Average Response Time", "Request Count", "Failure Count"]]
    stats.rename(columns={"Average Response Time": "Response Time"}, inplace=True)

    markdown("### Summary Stats")
    if stats.shape[1] > 0:
        summary_stats = stats.aggregate(
            {
                "Request Count": ["sum"],
                "Failure Count": ["sum"],
                "Response Time": ["mean", "min", "max"],
            }
        )
        display_df(summary_stats)

    markdown("### Ten Worst Average Response Times")
    display_df(stats.sort_values(by=["Response Time"], ascending=False), 10)

    markdown("### Ten Best Average Response Times")
    display_df(stats.sort_values(by=["Response Time"], ascending=True), 10)


def run_analysis() -> None:

    results_dir = select_directory()

    _display_exceptions(results_dir)
    _display_failures(results_dir)
    _display_stats(results_dir)
