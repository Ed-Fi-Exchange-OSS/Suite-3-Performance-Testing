import factory

from edfi_performance.api.client.education import LocalEducationAgencyClient
from edfi_performance.api.client.school import SchoolClient
from .. import APIFactory
from ..descriptors.utils import build_descriptor, build_descriptor_dicts
from ..utils import RandomSuffixAttribute, current_year


class CourseFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )
    academicSubjectDescriptor = build_descriptor('AcademicSubject', 'Mathematics')
    courseTitle = 'Algebra I'
    courseCode = RandomSuffixAttribute('03100500')
    numberOfParts = 1
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            'courseIdentificationSystem',
            [('State course code', {'identificationCode': o.courseCode})]
        )
    )
    levelCharacteristics = factory.List([
        factory.Dict(
            dict(
                courseLevelCharacteristicDescriptor=build_descriptor('courseLevelCharacteristic', 'Core Subject')
            )
        ),
    ])


class CourseTranscriptFactory(APIFactory):
    courseReference = factory.Dict(
        dict(
            educationOrganizationId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
            courseCode='ELA-01',
        ),
    )
    studentAcademicRecordReference = factory.Dict(
        dict(
            educationOrganizationId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            studentUniqueId=111111,  # Default value for scenarios, but not in DB
            termDescriptor=build_descriptor('Term', 'Fall Semester'),
        ),
    )
    courseAttemptResultDescriptor = build_descriptor('CourseAttemptResult', 'Pass')
    finalLetterGradeEarned = "B"
    finalNumericGradeEarned = 83
