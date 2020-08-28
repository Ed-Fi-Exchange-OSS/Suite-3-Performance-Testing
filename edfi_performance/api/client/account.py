# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient


class AccountCodeClient(EdFiAPIClient):
    endpoint = 'accountCodes'


class AccountClient(EdFiAPIClient):
    endpoint = 'accounts'

    dependencies = {
        AccountCodeClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        account_code_reference = self.account_code_client.create_with_dependencies()
        account_code_attrs = account_code_reference['attributes']

        edorg_id = account_code_attrs['educationOrganizationReference']['educationOrganizationId']
        account_attrs = self.factory.build_dict(
            accountCodes=[{
                'accountCodeReference': dict(
                    accountCodeNumber=account_code_attrs['accountCodeNumber'],
                    educationOrganizationId=edorg_id,
                    accountClassificationDescriptor=account_code_attrs['accountClassificationDescriptor'],
                    fiscalYear=account_code_attrs['fiscalYear'],
                ),
            }],
            educationOrganizationReference__educationOrganizationId=edorg_id,
            fiscalYear=account_code_attrs['fiscalYear'],
        )
        account_id = self.create(**account_attrs)

        return {
            'resource_id': account_id,
            'dependency_ids': {
                'account_code_id': account_code_reference['resource_id'],
            },
            'attributes': account_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.account_code_client.delete(reference['dependency_ids']['account_code_id'])


class _AccountDependentMixin(object):
    """
    Base class for clients for all resources dependent solely on Account
    """
    dependencies = {
        AccountClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        account_reference = self.account_client.create_with_dependencies()
        account_identifier = account_reference['attributes']['accountIdentifier']

        resource_attrs = self.factory.build_dict(
            accountReference__accountIdentifier=account_identifier,
            **kwargs
        )
        resource_id = self.create(**resource_attrs)

        return {
            'resource_id': resource_id,
            'dependency_ids': {
                'account_reference': account_reference,
            },
            'attributes': resource_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.account_client.delete_with_dependencies(reference['dependency_ids']['account_reference'])


class ActualClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = 'actuals'


class BudgetClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = 'budgets'


class ContractedStaffClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = 'contractedStaffs'


class PayrollClient(_AccountDependentMixin, EdFiAPIClient):
    endpoint = 'payrolls'
