# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path

import pandas as pd
from edfi_perf_test_analysis.ui_helpers import markdown, display_df


def display_exceptions(results_dir: str, test_type: str) -> None:
    exceptions = pd.read_csv(path.join(results_dir, f"{test_type}_exceptions.csv"))

    markdown("### Exceptions")
    markdown("First five exceptions")
    display_df(exceptions, 5)


def display_failures(results_dir: str, test_type: str) -> None:
    failures = pd.read_csv(path.join(results_dir, f"{test_type}_failures.csv"))

    markdown("### Failures")
    markdown("First ten failures")
    display_df(failures, 10)


def get_and_prep_stats(results_dir: str, test_type: str) -> pd.DataFrame:
    stats = pd.read_csv(path.join(results_dir, f"{test_type}_stats.csv"))

    # Remove the "Aggregated" row
    stats.drop(stats.index[stats["Name"] == "Aggregated"], inplace=True)

    # Create a new column combining Type and Name, then index on it
    stats["Request"] = stats["Type"] + " " + stats["Name"]
    stats.set_index("Request", inplace=True)

    # Use the 95% "empirical rule" to approximate the standard error (Dev)
    # https://online.stat.psu.edu/stat200/lesson/2/2.2/2.2.7
    stats["Approx Std Dev"] = (stats["95%"] - stats["Average Response Time"]) / 2

    # Keep only the columns we care about
    stats = stats[
        ["Average Response Time", "Request Count", "Failure Count", "Approx Std Dev"]
    ]
    stats.rename(columns={"Average Response Time": "Response Time"}, inplace=True)

    return stats


def get_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    return df.aggregate(
        {
            "Request Count": ["sum"],
            "Failure Count": ["sum"],
            "Response Time": ["mean", "min", "max"],
            "Approx Std Dev": ["mean", "min", "max"],
        }
    )


def display_stats(results_dir: str, test_type: str) -> pd.DataFrame:

    stats = get_and_prep_stats(results_dir, test_type)

    if stats.shape[1] == 0:
        raise RuntimeError(f"No {test_type} data available in {results_dir}")

    markdown("### Summary Stats")
    display_df(get_summary_stats(stats))

    markdown("### Ten Worst Average Response Times")
    display_df(stats.sort_values(by=["Response Time"], ascending=False), 10)

    markdown("### Ten Best Average Response Times")
    display_df(stats.sort_values(by=["Response Time"], ascending=True), 10)

    return stats
