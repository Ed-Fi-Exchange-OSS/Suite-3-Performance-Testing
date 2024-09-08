# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.api.client.program import ProgramClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.api.client.staff import StaffClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import (
    build_descriptor,
    build_descriptor_dicts,
)
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
    formatted_date,
    current_year,
    RandomDateAttribute,
)


class OpenStaffPositionFactory(APIFactory):
    requisitionNumber = UniqueIdAttribute(num_chars=20)
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=SchoolClient.shared_elementary_school_id())
    )
    employmentStatusDescriptor = build_descriptor(
        "EmploymentStatus", "Substitute/temporary"
    )
    staffClassificationDescriptor = build_descriptor(
        "StaffClassification", "Substitute Teacher"
    )
    datePosted = formatted_date(3, 17)


class StaffEducationOrganizationAssignmentAssociationFactory(APIFactory):
    staffReference = factory.Dict(dict(staffUniqueId=None))  # Must be entered by user
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    staffClassificationDescriptor = build_descriptor("StaffClassification", "Teacher")
    positionTitle = "1st Grade teacher"
    beginDate = RandomDateAttribute()
    endDate = formatted_date(1, 3)


class StaffFactory(APIFactory):
    staffUniqueId = UniqueIdAttribute()
    firstName = "John"
    middleName = "Michael"
    lastSurname = "Loyo"
    hispanicLatinoEthnicity = True
    birthDate = "1959-04-30"
    generationCodeSuffix = "Sr"
    highestCompletedLevelOfEducationDescriptor = build_descriptor(
        "LevelOfEducationDescriptor", "Master's"
    )
    highlyQualifiedTeacher = True
    personalTitlePrefix = "Mr"
    sexDescriptor = build_descriptor("Sex", "Male")
    electronicMails = factory.List(
        [
            dict(
                electronicMailAddress="johnloyo@edficert.org",
                electronicMailTypeDescriptor=build_descriptor(
                    "ElectronicMailType", "Work"
                ),
            ),
        ]
    )
    identificationCodes = factory.LazyAttribute(
        lambda o: build_descriptor_dicts(
            "staffIdentificationSystem",
            [("State", {"identificationCode": o.staffUniqueId})],
        )
    )
    languages = factory.List(
        [
            dict(
                languageDescriptor=build_descriptor("Language", "spa"),
            ),
        ]
    )


class StaffAbsenceEventFactory(APIFactory):
    absenceEventCategoryDescriptor = build_descriptor(
        "AbsenceEventCategory", "Vacation"
    )
    eventDate = RandomDateAttribute()
    staffReference = factory.Dict(dict(staffUniqueId=StaffClient.shared_staff_id()))
    absenceEventReason = "Vacationing in Hawai'i"


class StaffCohortAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    staffReference = factory.Dict(dict(staffUniqueId=None))  # Must be entered by user
    cohortReference = factory.Dict(
        dict(
            cohortIdentifier=None,
            educationOrganizationId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school record
        )
    )  # Must be provided by caller


class StaffEducationOrganizationContactAssociationFactory(APIFactory):
    contactTitle = UniqueIdAttribute(num_chars=75)
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff record
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    electronicMailAddress = "staff@school.edu"


class StaffEducationOrganizationEmploymentAssociationFactory(APIFactory):
    employmentStatusDescriptor = build_descriptor(
        "EmploymentStatus", "Substitute/temporary"
    )
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff record
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    hireDate = RandomDateAttribute()
    hourlyWage = 20.0


class StaffLeaveFactory(APIFactory):
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff record
    staffLeaveEventCategoryDescriptor = build_descriptor(
        "StaffLeaveEventCategory", "Bereavement"
    )
    beginDate = RandomDateAttribute()
    reason = "Family emergency"


class StaffProgramAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff record
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programName=ProgramClient.shared_program_name(),
            programTypeDescriptor=build_descriptor(
                "ProgramType", ProgramClient.shared_program_name()
            ),
        )
    )  # Prepopulated program
    studentRecordAccess = True


class StaffSchoolAssociationFactory(APIFactory):
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff record
    schoolReference = factory.Dict(
        dict(schoolId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school record
    academicSubjects = factory.List(
        [
            dict(
                academicSubjectDescriptor=build_descriptor(
                    "AcademicSubject", "English Language Arts"
                )
            ),
        ]
    )
    gradeLevels = factory.List([])  # Default grade levels are blank for scenario
    programAssignmentDescriptor = build_descriptor(
        "ProgramAssignment", "Other"
    )  # Required despite "optional" in docs


class StaffSectionAssociationFactory(APIFactory):
    sectionReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            sectionIdentifier="ELA012017RM555",
            sessionName="2016-2017 Fall Semester",
        )
    )
    staffReference = factory.Dict(
        dict(staffUniqueId=StaffClient.shared_staff_id())
    )  # Prepopulated staff record
    classroomPositionDescriptor = build_descriptor(
        "ClassroomPosition", "Teacher of Record"
    )
    beginDate = formatted_date(8, 31)
