# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class AccountCodeClient(EdFiAPIClient):
    endpoint = "accountCodes"


class AccountClient(EdFiAPIClient):
    endpoint = "accounts"

    dependencies: Dict = {
        AccountCodeClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        # TODO: this is the only reference to account_code_client anywhere in
        # the code base, so the next line should fail if it is ever called.
        account_code_reference = self.account_code_client.create_with_dependencies()
        account_code_attrs = account_code_reference["attributes"]

        edorg_id = account_code_attrs["educationOrganizationReference"][
            "educationOrganizationId"
        ]
        return self.create_using_dependencies(
            account_code_reference,
            accountCodes=[
                {
                    "accountCodeReference": dict(
                        accountCodeNumber=account_code_attrs["accountCodeNumber"],
                        educationOrganizationId=edorg_id,
                        accountClassificationDescriptor=account_code_attrs[
                            "accountClassificationDescriptor"
                        ],
                        fiscalYear=account_code_attrs["fiscalYear"],
                    ),
                }
            ],
            educationOrganizationReference__educationOrganizationId=edorg_id,
            fiscalYear=account_code_attrs["fiscalYear"],
        )


class _AccountDependentMixin(object):
    """
    Base class for clients for all resources dependent solely on Account
    """

    dependencies: Dict = {
        AccountClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        account_reference = self.account_client.create_with_dependencies()
        account_identifier = account_reference["attributes"]["accountIdentifier"]

        return self.create_using_dependencies(
            account_reference,
            accountReference__accountIdentifier=account_identifier,
            **kwargs
        )


class ActualClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = "actuals"


class BudgetClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = "budgets"


class ContractedStaffClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = "contractedStaffs"


class PayrollClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = "payrolls"
