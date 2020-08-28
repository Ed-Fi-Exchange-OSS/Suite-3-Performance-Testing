# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from edfi_performance.api.client.staff import StaffClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import UniqueIdAttribute, current_year, formatted_date


class AccountFactory(APIFactory):
    accountIdentifier = UniqueIdAttribute()
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    accountCodes = factory.List([
        factory.Dict({  # Values for a prepopulated account, but don't rely on this existing
            'accountCodeReference': dict(
                accountCodeNumber="1000",
                educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
                accountClassificationDescriptor=build_descriptor('AccountClassification', 'Function'),
                fiscalYear=current_year(),
            )
        }),
    ])
    fiscalYear = current_year()


class AccountCodeFactory(APIFactory):
    accountCodeNumber = UniqueIdAttribute()
    educationOrganizationReference = factory.Dict(dict(educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()))
    accountClassificationDescriptor = build_descriptor('AccountClassification', 'Function')
    fiscalYear = current_year()
    accountCodeDescription = "Instruction"


class ActualFactory(APIFactory):
    accountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    asOfDate = formatted_date(8, 13)
    amountToDate = 123.45


class BudgetFactory(APIFactory):
    accountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    asOfDate = formatted_date(10, 11)
    amount = 1000.00


class ContractedStaffFactory(APIFactory):
    accountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    staffReference = factory.Dict(dict(staffUniqueId=StaffClient.shared_staff_id()))  # Prepopulated staff
    asOfDate = formatted_date(4, 27)
    amountToDate = 187.00


class PayrollFactory(APIFactory):
    accountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    staffReference = factory.Dict(dict(staffUniqueId=StaffClient.shared_staff_id()))  # Prepopulated staff
    asOfDate = formatted_date(12, 27)
    amountToDate = 271.83
