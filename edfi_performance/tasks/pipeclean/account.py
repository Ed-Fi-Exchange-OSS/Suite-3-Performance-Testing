# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class AccountPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'fiscalYear'
    update_attribute_value = 2011


class AccountCodePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'accountClassificationDescriptor'
    update_attribute_value = build_descriptor('AccountClassification', 'Fund')


class ActualPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'amountToDate'
    update_attribute_value = 456.78


class BudgetPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'amount'
    update_attribute_value = 2000.00


class ContractedStaffPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'amountToDate'
    update_attribute_value = 1137.00


class PayrollPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'amountToDate'
    update_attribute_value = 314.16
