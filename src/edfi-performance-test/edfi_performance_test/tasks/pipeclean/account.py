# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)
from edfi_performance_test.factories.utils import current_year


class AccountPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "fiscalYear"
    update_attribute_value = current_year()


class AccountCodePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "accountCodeDescription"
    update_attribute_value = "another description"


class ActualPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amountToDate"
    update_attribute_value = 456.78


class BudgetPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amount"
    update_attribute_value = 2000.00


class ContractedStaffPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amountToDate"
    update_attribute_value = 1137.00


class PayrollPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amountToDate"
    update_attribute_value = 314.16
