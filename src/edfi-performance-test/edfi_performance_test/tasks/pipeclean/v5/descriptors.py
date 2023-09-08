# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.pipeclean.descriptors import (
    OldEthnicityPipecleanTest,
    DescriptorPipecleanTestBase,
)


class SkipOldEthnicityPipecleanTest(OldEthnicityPipecleanTest):
    @classmethod
    def skip_all_scenarios(cls):
        return True


class EligibilityDelayReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EligibilityDelayReasonPipecleanTest, self).__init__(
            "eligibilityDelayReason", parent, *args, **kwargs
        )


class EligibilityEvaluationTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EligibilityEvaluationTypePipecleanTest, self).__init__(
            "eligibilityEvaluationType", parent, *args, **kwargs
        )


class EnrollmentTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EnrollmentTypePipecleanTest, self).__init__(
            "enrollmentType", parent, *args, **kwargs
        )


class EvaluationDelayReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EvaluationDelayReasonPipecleanTest, self).__init__(
            "evaluationDelayReason", parent, *args, **kwargs
        )


class IdeaPartPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(IdeaPartPipecleanTest, self).__init__(
            "ideaPart", parent, *args, **kwargs
        )


class ProgramEvaluationPeriodPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramEvaluationPeriodPipecleanTest, self).__init__(
            "programEvaluationPeriod", parent, *args, **kwargs
        )


class ProgramEvaluationTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramEvaluationTypePipecleanTest, self).__init__(
            "programEvaluationType", parent, *args, **kwargs
        )


class RatingLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RatingLevelPipecleanTest, self).__init__(
            "ratingLevel", parent, *args, **kwargs
        )


class SchoolChoiceBasisPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SchoolChoiceBasisPipecleanTest, self).__init__(
            "schoolChoiceBasis", parent, *args, **kwargs
        )
