# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.student import StudentClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import RandomDateAttribute, RandomSuffixAttribute, UniqueIdAttribute


class AssessmentFactory(APIFactory):
    assessmentIdentifier = UniqueIdAttribute()
    academicSubjects = factory.List([
        factory.Dict(
            dict(
                academicSubjectDescriptor=build_descriptor('AcademicSubject', 'English')
            )
        )
    ])
    assessedGradeLevels = factory.List([
        factory.Dict(
            dict(
                gradeLevelDescriptor=build_descriptor('GradeLevel', 'Twelfth grade')
            )
        )
    ])
    assessmentTitle = RandomSuffixAttribute("AP - English")
    assessmentVersion = 2017
    maxRawScore = 25
    namespace = 'uri://ed-fi.org/Assessment/Assessment.xml'
    identificationCodes = factory.List([
        factory.Dict(
            dict(
                assessmentIdentificationSystemDescriptor=build_descriptor(
                    'AssessmentIdentificationSystem', 'Test Contractor'),
                identificationCode="AP English",
            )
        ),
    ])
    performanceLevels = factory.List([
        factory.Dict(
            dict(
                assessmentReportingMethodDescriptor=build_descriptor('AssessmentReportingMethod', 'Scale score'),
                performanceLevelDescriptor=build_descriptor('PerformanceLevel', 'Pass'),
                maximumScore="25",
                minimumScore="12",
            )
        ),
        factory.Dict(
            dict(
                assessmentReportingMethodDescriptor=build_descriptor('AssessmentReportingMethod', 'Scale score'),
                performanceLevelDescriptor=build_descriptor('PerformanceLevel', 'Fail'),
                maximumScore="11",
                minimumScore="0",
            )
        ),
    ])
    scores = factory.List([
        factory.Dict(
            dict(
                assessmentReportingMethodDescriptor=build_descriptor('AssessmentReportingMethod', 'Scale score'),
                resultDatatypeType="Integer",
                maximumScore="25",
                minimumScore="0",
            )
        ),
    ])


class AssessmentItemFactory(APIFactory):
    assessmentReference = factory.Dict(
        dict(
            assessmentIdentifier=None,
            namespace='uri://ed-fi.org/Assessment/Assessment.xml'
        )
    )
    identificationCode = UniqueIdAttribute()
    assessmentItemCategoryDescriptor = build_descriptor('AssessmentItemCategory', 'List Question')
    correctResponse = 'A'
    maxRawScore = 1


class LearningObjectiveFactory(APIFactory):
    academicSubjects = factory.List([
        factory.Dict(
            dict(
                academicSubjectDescriptor=build_descriptor('AcademicSubject', 'Mathematics'),
                namespace='uri://ed-fi.org/'
            )
        )
    ])
    objective = RandomSuffixAttribute("Number Operations and Concepts")
    gradeLevels = factory.List([
        factory.Dict(
            dict(
                gradeLevelDescriptor=build_descriptor('GradeLevel', 'Sixth grade')
            )
        )
    ])
    description = (
        "The student will demonstrate the ability to utilize numbers to perform"
        " operations with complex concepts."
    )
    learningObjectiveId = UniqueIdAttribute()
    namespace = 'uri://ed-fi.org'


class LearningStandardFactory(APIFactory):
    learningStandardId = UniqueIdAttribute()
    academicSubjects = factory.List([
        factory.Dict(
            dict(academicSubjectDescriptor=build_descriptor('AcademicSubject', 'Mathematics'))
        )
    ])
    courseTitle = "Advanced Math for students v4.4"
    description = "Unit 1 Advanced Math for students v4.4"
    namespace = 'uri://ed-fi.org/LearningStandard/LearningStandard.xml'
    gradeLevels = factory.List([
        factory.Dict(
            dict(gradeLevelDescriptor=build_descriptor('GradeLevel', 'Tenth grade'))
        ),
    ])


class ObjectiveAssessmentFactory(APIFactory):
    assessmentReference = factory.Dict(
        dict(
            assessmentIdentifier=None,
            namespace='uri://ed-fi.org/Assessment/Assessment.xml'
        )
    )
    identificationCode = UniqueIdAttribute()
    maxRawScore = 8


class StudentAssessmentFactory(APIFactory):
    studentAssessmentIdentifier = UniqueIdAttribute()
    studentReference = factory.Dict(dict(studentUniqueId=StudentClient.shared_student_id()))  # Prepopulated student
    assessmentReference = factory.Dict(
        dict(
            assessmentIdentifier=None,
            namespace='uri://ed-fi.org/Assessment/Assessment.xml'
        )
    )
    administrationDate = RandomDateAttribute()  # Along with studentReference and assessmentReference, this is the PK
    administrationEnvironmentDescriptor = build_descriptor('AdministrationEnvironment', 'Testing Center')
    administrationLanguageDescriptor = build_descriptor('Language', 'eng')
    serialNumber = "0"
    whenAssessedGradeLevelDescriptor = build_descriptor('GradeLevel', 'Sixth grade')
    performanceLevels = factory.List([
        factory.Dict(
            dict(
                assessmentReportingMethodDescriptor=build_descriptor('AssessmentReportingMethod', 'Scale score'),
                performanceLevelDescriptor=build_descriptor('PerformanceLevel', 'Fail'),
                performanceLevelMet=True,
            )
        ),
    ])
    scoreResults = factory.List([
        factory.Dict(
            dict(
                assessmentReportingMethodDescriptor=build_descriptor('AssessmentReportingMethod', 'Scale score'),
                result="25",
                resultDatatypeTypeDescriptor=build_descriptor('ResultDatatypeType', 'Integer'),
            )
        )
    ])
