# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path, scandir
from typing import Optional
from tkinter import Tk, filedialog

from IPython.display import display, Markdown, HTML
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

    display(
        HTML(
            df.fillna("")
            .style.format(precision=2)
            .set_properties(**{"text-align": "left"})
            .set_table_styles([dict(selector="th", props=[("text-align", "left")])])
            .to_html(index=False, max_rows=max_rows)
        )
    )


def select_directory(def_dir="") -> str:
    if def_dir == "":
        root = Tk()
        # Hide the main window
        root.withdraw()
        # Raise the root to the top of all windows.
        root.call("wm", "attributes", ".", "-topmost", True)

        file_path = filedialog.askdirectory()
        root.destroy()
    else:
        file_path = def_dir

    if not path.exists(file_path):
        raise RuntimeError(
            f"Directory `{file_path}` does not exist or could not be read."
        )

    directories = sorted([f.path for f in scandir(file_path) if f.is_dir()])

    results_dir: str
    if len(directories) == 0:
        # Assume this directory has the test results
        results_dir = file_path
    else:
        # Sorted oldest to newest, so analyze the _last_ item as newest
        results_dir = directories[-1]

    log_info(f"Running analysis on {path.abspath(results_dir)}")

    return path.abspath(results_dir)
