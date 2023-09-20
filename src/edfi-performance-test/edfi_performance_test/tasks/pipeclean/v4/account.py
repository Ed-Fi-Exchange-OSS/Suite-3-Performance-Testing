# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.account import (
    AccountPipecleanTest,
    AccountCodePipecleanTest,
    ActualPipecleanTest,
    BudgetPipecleanTest,
    ContractedStaffPipecleanTest,
    PayrollPipecleanTest,
)
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)
from edfi_performance_test.factories.utils import current_year


class SkipAccountPipecleanTest(AccountPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipAccountCodePipecleanTest(AccountCodePipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipActualPipecleanTest(ActualPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipBudgetPipecleanTest(BudgetPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipContractedStaffPipecleanTest(ContractedStaffPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class SkipPayrollPipecleanTest(PayrollPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class LocalAccountPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "fiscalYear"
    update_attribute_value = current_year()


class LocalActualPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amount"
    update_attribute_value = 456.78


class LocalBudgetPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amount"
    update_attribute_value = 2000.00


class LocalContractedStaffPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amount"
    update_attribute_value = 1137.00


class LocalPayrollPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amount"
    update_attribute_value = 314.16


class LocalEncumbrancePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = "amount"
    update_attribute_value = 752.75
