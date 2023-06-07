# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.factories.resources.api_factory import APIFactory


class ChartOfAccountClient(EdFiAPIClient):
    if APIFactory.version.startswith("4"):
        endpoint = "chartOfAccounts"
    else:
        endpoint = "NoEndpoint"
