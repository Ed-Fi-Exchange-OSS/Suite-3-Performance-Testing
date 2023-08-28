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
