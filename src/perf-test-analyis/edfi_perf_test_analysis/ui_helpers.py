# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path, scandir
from typing import Optional, Callable

from IPython.display import display, Markdown, HTML
import ipywidgets as widgets
import pandas as pd

def markdown(message: str) -> None:
    display(Markdown(message))


def log_info(message: str) -> None:
    markdown(f"✅ **{message}**")


def log_warning(message: str) -> None:
    markdown(f"❕ **{message}**")


def log_error(message: str) -> None:
    markdown(f"❌ **{message}**")


def display_df(df: pd.DataFrame, max_rows: Optional[int] = None) -> None:

    if df.shape[0] == 0:
        log_warning("No data to display")
        return

    display(HTML(
      df.fillna("")
        .style
        .format(precision=2)
        .set_properties(**{'text-align': 'left'})
        .set_table_styles([dict(selector='th', props=[('text-align', 'left')])])
        .to_html(index=False, max_rows=max_rows)
    ))


def select_dir_and_run(callback: Callable[[str], None]) -> None:
    results_path = widgets.Text(value="../../../testResults", description="Results Path:")
    run = widgets.Button(
        description="Run", button_style="primary"
    )

    output: widgets.Output = widgets.Output()
    display(results_path, run, output)

    def __on_click(_: widgets.Button) -> None:
        with output:
            output.clear_output()
            file_path = results_path.value

            if not path.exists(file_path):
                log_error(f"Directory `{file_path}` does not exist or could not be read.")
                return

            directories = sorted([
                f.path
                for f in scandir(file_path)
                if f.is_dir()
            ])

            results_dir: str
            if len(directories) == 0:
                # Assume this directory has the test results
                results_dir = file_path
            else:
                # Sorted oldest to newest, so analyze the _last_ item as newest
                results_dir = directories[-1]

            log_info(f"Running analysis on {path.abspath(results_dir)}")

            callback(file_path)

    run.on_click(__on_click)
