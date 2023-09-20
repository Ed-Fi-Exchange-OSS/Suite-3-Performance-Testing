# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust.clients import HttpSession
from edfi_performance_test.api.client.descriptors import (
    DescriptorClient,
)


class DescriptorClientV5(DescriptorClient):
    def __init__(self, client: HttpSession, token: str = ""):
        super(DescriptorClient, self).__init__(client, token)
