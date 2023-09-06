# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.descriptors import (
    AccountClassificationPipecleanTest,
    DescriptorPipecleanTestBase,
)


class SkipAccountClassificationPipecleanTest(AccountClassificationPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class AccountTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AccountTypePipecleanTest, self).__init__(
            "accountType", parent, *args, **kwargs
        )


class AssignmentLateStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssignmentLateStatusPipecleanTest, self).__init__(
            "assignmentLateStatus", parent, *args, **kwargs
        )


class EducationOrganizationAssociationTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EducationOrganizationAssociationTypePipecleanTest, self).__init__(
            "educationOrganizationAssociationType", parent, *args, **kwargs
        )


class FinancialCollectionPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(FinancialCollectionPipecleanTest, self).__init__(
            "financialCollection", parent, *args, **kwargs
        )


class ModelEntityPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ModelEntityPipecleanTest, self).__init__(
            "modelEntity", parent, *args, **kwargs
        )


class ReportingTagPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ReportingTagPipecleanTest, self).__init__(
            "reportingTag", parent, *args, **kwargs
        )


class SubmissionStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SubmissionStatusPipecleanTest, self).__init__(
            "submissionStatus", parent, *args, **kwargs
        )
