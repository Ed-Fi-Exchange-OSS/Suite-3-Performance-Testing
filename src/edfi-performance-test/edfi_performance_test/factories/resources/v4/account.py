# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.api.client.staff import StaffClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
    current_year,
    formatted_date,
)


class LocalAccountFactory(APIFactory):
    accountIdentifier = UniqueIdAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )
    chartOfAccountReference = factory.Dict(
        dict(
            accountIdentifier=factory.Dict(dict(accountIdentifier=None)),
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    fiscalYear = current_year()


class LocalActualFactory(APIFactory):
    asOfDate = formatted_date(8, 13)
    localAccountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    amount = 123.45


class LocalBudgetFactory(APIFactory):
    localAccountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    asOfDate = formatted_date(10, 11)
    amount = 1000.00


class LocalContractedStaffFactory(APIFactory):
    localAccountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff
    asOfDate = formatted_date(4, 27)
    amount = 187.00


class LocalPayrollFactory(APIFactory):
    localAccountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff
    asOfDate = formatted_date(12, 27)
    amount = 271.83


class LocalEncumbranceFactory(APIFactory):
    localAccountReference = factory.Dict(
        dict(
            accountIdentifier=None,  # Must create an account to refer to
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            fiscalYear=current_year(),
        )
    )
    asOfDate = formatted_date(3, 21)
    amount = 586.10
