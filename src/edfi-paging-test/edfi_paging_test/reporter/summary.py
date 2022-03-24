# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from dataclasses import dataclass, field
from typing import List
import socket


@dataclass
class Summary:
    key: str
    description: str
    machine_name : str = socket.gethostname()
    resources: List[str] = field(default_factory=lambda: ["all"])

    def __post_init__(self):
        self.resources = (self.resources or ["all"])
