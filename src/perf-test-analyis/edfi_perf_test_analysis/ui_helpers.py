# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from os import path, scandir
from typing import Optional
from tkinter import Tk, filedialog

from IPython.display import display, Markdown, HTML
import pandas as pd
import os
import glob
from typing import Tuple

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


def select_directory() -> str:
    root = Tk()
    # Hide the main window
    root.withdraw()
    # Raise the root to the top of all windows.
    root.call("wm", "attributes", ".", "-topmost", True)

    file_path = filedialog.askdirectory()
    root.destroy()

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


def get_result_directory() -> Tuple[str, str]:

    result_dir_root = path.abspath('./notebook_input.txt')
    if not path.exists(result_dir_root):
         return ("","")

    with open(result_dir_root) as f:
        result_root_dir = f.read().rstrip('\n')

    result_dir = path.abspath(result_root_dir)

    name_list = os.listdir(result_dir)
    full_list = [os.path.join(result_dir, i) for i in name_list]
    time_sorted_list = sorted(full_list, key=os.path.getmtime)

    result_dir = time_sorted_list[-1]
    if len(time_sorted_list) > 1:
        all_files = os.listdir(result_dir)
        csv_files = list(filter(lambda f: f.endswith('.csv'), all_files))
        result_file = csv_files[0]

        index = -2
        #find compare directory with same type of test results as in the result_dir
        while not os.path.exists(os.path.join(time_sorted_list[index], result_file)):
            index = index - 1
        compare_dir = time_sorted_list[index]

    return (result_dir, compare_dir)
