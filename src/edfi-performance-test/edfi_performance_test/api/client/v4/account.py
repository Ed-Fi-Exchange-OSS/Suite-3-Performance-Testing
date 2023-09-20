# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class LocalAccountClient(EdFiAPIClient):
    endpoint = "localAccounts"

    dependencies: Dict = {
        "edfi_performance_test.api.client.v4.chart_of_account.ChartOfAccountClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        # Create chart of account
        chart_of_account_reference = self.chart_of_account_client.create_with_dependencies()

        # Get attributes
        account_code_attrs = chart_of_account_reference["attributes"]
        account_identifier = account_code_attrs["accountIdentifier"]

        edorg_id = account_code_attrs["educationOrganizationReference"][
            "educationOrganizationId"
        ]

        return self.create_using_dependencies(
            chart_of_account_reference,
            fiscalYear=account_code_attrs["fiscalYear"],
            chartOfAccountReference__accountIdentifier=account_identifier,
            chartOfAccountReference__educationOrganizationId=edorg_id,
            chartOfAccountReference__fiscalYear=account_code_attrs["fiscalYear"],
            educationOrganizationReference__educationOrganizationId=edorg_id
        )


class _LocalAccountDependentMixin(object):
    """
    Base class for clients for all resources dependent solely on LocalAccount
    """

    dependencies: Dict = {
        LocalAccountClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        account_reference = self.local_account_client.create_with_dependencies()
        account_identifier = account_reference["attributes"]["accountIdentifier"]
        edorg_id = account_reference["attributes"]["educationOrganizationReference"][
            "educationOrganizationId"
        ]

        return self.create_using_dependencies(
            account_reference,
            localAccountReference__accountIdentifier=account_identifier,
            localAccountReference__educationOrganizationId=edorg_id,
            **kwargs
        )


class LocalActualClient(_LocalAccountDependentMixin, EdFiAPIClient):
    endpoint = "localActuals"


class LocalBudgetClient(_LocalAccountDependentMixin, EdFiAPIClient):
    endpoint = "localBudgets"


class LocalContractedStaffClient(_LocalAccountDependentMixin, EdFiAPIClient):
    endpoint = "localContractedStaffs"


class LocalPayrollClient(_LocalAccountDependentMixin, EdFiAPIClient):
    endpoint = "localPayrolls"


class LocalEncumbranceClient(_LocalAccountDependentMixin, EdFiAPIClient):
    endpoint = "localEncumbrances"
