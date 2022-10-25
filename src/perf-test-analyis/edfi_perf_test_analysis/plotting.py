# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy

from edfi_perf_test_analysis.ui_helpers import markdown


def prepare_for_charts() -> None:
    sns.set_theme(style="darkgrid")


def regression_plot(df: pd.DataFrame, x: str, y: str) -> None:
    regression = sns.regplot(data=df, x=x, y=y, fit_reg=True)

    # Remove x-axis ticks and labels
    regression.set(xticklabels=[])
    regression.set(xlabel=None)
    regression.tick_params(bottom=False)

    plt.show()

    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(
        x=regression.get_lines()[0].get_xdata(), y=regression.get_lines()[0].get_ydata()
    )
    markdown(
        f"y=({round(slope, 4)})x + {round(intercept,4)}, r={round(r_value,4)}"
        f", p={round(p_value,4)}, std_err={round(std_err, 4)}"
    )
