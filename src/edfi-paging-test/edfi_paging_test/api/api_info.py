# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


from typing import List, Dict
from dataclasses import dataclass


@dataclass
class APIInfo:
    """
    Container for holding details from api version endpoint
    """

    version: str
    api_mode: str
    datamodels: List[Dict[str, str]]
    urls: Dict[str, str]

    @property
    def oauth_url(self) -> str:
        return self.urls["oauth"]

    @property
    def api_metadata_url(self) -> str:
        return self.urls["openApiMetadata"]
