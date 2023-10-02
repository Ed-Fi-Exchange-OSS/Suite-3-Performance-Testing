# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass
from edfi_paging_test.helpers.main_arguments import MainArguments
from pandas import DataFrame
import pandas as pd
import json
import socket


@dataclass
class Summary:
    run_name: str
    run_configration: MainArguments
    machine_name : str = socket.gethostname()

    def __post_init__(self):
        if (self.run_configration):
            self.run_configration.resourceList = (self.run_configration.resourceList or ["all"])
            self.run_configration.contentType = self.run_configration.contentType
            self.run_configration.log_level = self.run_configration.log_level

    def get_DataFrame(self) -> DataFrame:
        """
        Converts Summary to a DataFrame.

        Returns
        -------
        DataFrame
            A new DataFrame representing Summary
        """

        df = DataFrame(data=[self])
        json_summary = json.loads(df.to_json(orient="records"))  # type: ignore
        df = pd.json_normalize(json_summary)  # type: ignore
        df.columns = df.columns.str.title().str.replace("_", "")  # type: ignore
        return df
