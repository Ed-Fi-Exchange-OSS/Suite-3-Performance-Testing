# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.education import LocalEducationAgencyClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.resources.address import AddressFactory
from edfi_performance_test.factories.utils import (
    UniqueIdAttribute,
    formatted_date,
    current_year,
    RandomDateAttribute,
)


class StudentFactory(APIFactory):
    studentUniqueId = UniqueIdAttribute()
    birthDate = formatted_date(1, 1, 2009)
    firstName = "Austin"
    middleName = "Samuel"
    lastSurname = "Jones"
    generationCodeSuffix = "JR"
    personalTitlePrefix = "Mr"
    hispanicLatinoEthnicity = False
    birthCity = "Grand Bend"
    birthCountryDescriptor = build_descriptor("Country", "AG")
    birthStateAbbreviationDescriptor = build_descriptor("StateAbbreviation", "TX")
    addresses = factory.List(
        [
            factory.SubFactory(
                AddressFactory,
                addressTypeDescriptor=build_descriptor("AddressType", "Temporary"),
                city="Grand Bend",
                postalCode="78834",
                streetNumberName="654 Mission Hills",
                apartmentRoomSuiteNumber="100",
                nameOfCounty="Williston",
            )
        ]
    )
    electronicMails = factory.List(
        [
            dict(
                electronicMailAddress="Austin@edficert.org",
                electronicMailTypeDescriptor=build_descriptor(
                    "ElectronicMailType", "Other"
                ),
            ),
        ]
    )
    identificationCodes = factory.List(
        [
            dict(
                identificationCode=704,
                assigningOrganizationIdentificationCode="State",
                studentIdentificationSystemDescriptor=build_descriptor(
                    "StudentIdentificationSystem", "State"
                ),
            ),
        ]
    )
    studentLanguages = factory.List(
        [
            dict(
                languageDescriptor=build_descriptor("Language", "Spanish"),
            ),
        ]
    )
    studentLanguageUses = factory.List(
        [
            dict(
                languageUseDescriptor=build_descriptor("LanguageUse", "Home language"),
            ),
        ]
    )
    studentRaces = factory.List(
        [
            dict(raceDescriptor=build_descriptor("Race", "Black - African American")),
        ]
    )
    telephones = factory.List(
        [
            dict(
                telephoneNumber="111-222-3333",
                telephoneNumberTypeDescriptor=build_descriptor(
                    "TelephoneNumberType", "Home"
                ),
            ),
        ]
    )


class StudentCohortAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    cohortReference = factory.Dict(
        dict(
            cohortIdentifier="1",  # Default value for scenarios, but not in DB
            educationOrganizationId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
        )
    )
    beginDate = RandomDateAttribute()


class StudentDisciplineIncidentAssociationFactory(APIFactory):
    disciplineIncidentReference = factory.Dict(
        dict(
            incidentIdentifier=None,  # Must be entered by user
            schoolId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
        ),
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=111111),  # Default value for scenarios, but not in DB
    )
    studentParticipationCodeDescriptor = build_descriptor(
        "StudentParticipationCode", "Perpetrator"
    )


class StudentEducationOrganizationAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Default ed org
    limitedEnglishProficiencyDescriptor = build_descriptor(
        "LimitedEnglishProficiency", "NotLimited"
    )
    studentCharacteristics = factory.List(
        [
            dict(
                studentCharacteristicDescriptor=build_descriptor(
                    "StudentCharacteristic", "Immigrant"
                ),
            ),
        ]
    )
    studentIndicators = factory.List(
        [
            dict(
                indicatorName="At Risk",
                indicator=True,
            ),
        ]
    )
    sexDescriptor = build_descriptor("Sex", "Male")


class StudentParentAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    parentReference = factory.Dict(dict(parentUniqueId=None))  # Must be entered by user
    emergencyContactStatus = True
    primaryContactStatus = True
    relationDescriptor = build_descriptor("Relation", "Father")


class StudentProgramAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed organization
    programReference = factory.Dict(
        dict(
            programTypeDescriptor=build_descriptor(
                "ProgramType", "Gifted and Talented"
            ),
            programName="Gifted and Talented",
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),  # Prepopulated ed organization
        )
    )
    beginDate = formatted_date(8, 23)


class StudentSchoolAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    schoolReference = factory.Dict(
        dict(schoolId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    entryDate = RandomDateAttribute()
    entryGradeLevelDescriptor = build_descriptor("GradeLevel", "First Grade")
    classOfSchoolYearTypeReference = factory.Dict(dict(schoolYear=2027))
    schoolYear = current_year()
    entryTypeDescriptor = build_descriptor("EntryType", "Next year school")
    repeatGradeIndicator = False
    residencyStatusDescriptor = build_descriptor(
        "ResidencyStatus", "Resident of admin unit and school area"
    )
    schoolChoiceTransfer = False


class StudentTitleIPartAProgramAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed organization
    programReference = factory.Dict(
        dict(
            programTypeDescriptor=build_descriptor("ProgramType", "Title I Part A"),
            programName="Title I Part A",
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),  # Prepopulated ed organization
        )
    )
    beginDate = formatted_date(8, 23)
    titleIPartAParticipantDescriptor = build_descriptor(
        "TitleIPartAParticipant", "Public Targeted Assistance Program"
    )


class StudentSpecialEducationProgramAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed organization
    programReference = factory.Dict(
        dict(
            programTypeDescriptor=build_descriptor("ProgramType", "Special Education"),
            programName="Special Education",
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),  # Prepopulated ed organization
        )
    )
    beginDate = formatted_date(8, 23)
    specialEducationSettingDescriptor = build_descriptor(
        "SpecialEducationSetting", "Inside regular class 80% or more of the day"
    )
    ideaEligibility = True


class StudentSectionAssociationFactory(APIFactory):
    sectionReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            sectionIdentifier="ELA012017RM555",
            sessionName="2016-2017 Fall Semester",
        )
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    beginDate = formatted_date(8, 23)
    endDate = formatted_date(12, 16)
    homeroomIndicator = False


class StudentSchoolAttendanceEventFactory(APIFactory):
    schoolReference = factory.Dict(
        dict(schoolId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    sessionReference = factory.Dict(
        dict(
            schoolId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
            schoolYear=2014,  # Prepopulated schoolYear
            sessionName="2016-2017 Fall Semester",  # Default value for scenarios, but not in the DB
        )
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    attendanceEventCategoryDescriptor = build_descriptor(
        "AttendanceEventCategory", "Tardy"
    )
    eventDate = formatted_date(9, 16)


class StudentSectionAttendanceEventFactory(APIFactory):
    sectionReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            sectionIdentifier="ELA012017RM555",
            sessionName="2016-2017 Fall Semester",
        )
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    attendanceEventCategoryDescriptor = build_descriptor(
        "AttendanceEventCategory", "Tardy"
    )
    eventDate = formatted_date(9, 16)
    attendanceEventReason = "No Note"


class StudentAcademicRecordFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    schoolYearTypeReference = factory.Dict(dict(schoolYear=current_year()))
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    termDescriptor = build_descriptor("Term", "Fall Semester")
    cumulativeAttemptedCredits = 0
    cumulativeEarnedCredits = 0


class StudentCompetencyObjectiveFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    gradingPeriodReference = factory.Dict(
        dict(
            schoolId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
            schoolYear=2014,  # Prepopulated schoolYear
            periodSequence=None,  # Must be entered by the user
            gradingPeriodDescriptor=build_descriptor(
                "GradingPeriod", "First Six Weeks"
            ),
        )
    )
    objectiveCompetencyObjectiveReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),  # Prepopulated ed org
            objective=None,  # Must be entered by the user
            objectiveGradeLevelDescriptor=build_descriptor("GradeLevel", "Tenth grade"),
        )
    )
    competencyLevelDescriptor = build_descriptor("CompetencyLevel", "Proficient")


class StudentCTEProgramAssociationFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    beginDate = RandomDateAttribute()
    nonTraditionalGenderStatus = True


class StudentEducationOrganizationResponsibilityAssociationFactory(APIFactory):
    educationOrganizationReference = factory.Dict(
        dict(educationOrganizationId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    beginDate = RandomDateAttribute()
    responsibilityDescriptor = build_descriptor("Responsibility", "Graduation")
    endDate = formatted_date(8, 8)


class StudentGradebookEntryFactory(APIFactory):
    numericGradeEarned = 80
    gradebookEntryReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            sectionIdentifier="ELA012017RM555",
            sessionName="2016-2017 Fall Semester",
            gradebookEntryTitle="ALG-1 - First Six Weeks - Homework - 20170821",
            dateAssigned=formatted_date(2, 2),
        )
    )  # Must be entered by user
    studentSectionAssociationReference = factory.Dict(
        dict(
            localCourseCode="ELA-01",
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=current_year(),
            sectionIdentifier="ELA012017RM555",
            sessionName="2016-2017 Fall Semester",
            studentUniqueId=111111,
            beginDate=formatted_date(5, 5),
        )
    )  # Must be entered by user


class StudentHomelessProgramAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    awaitingFosterCare = True


class StudentInterventionAssociationFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    interventionReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            interventionIdentificationCode=None,  # Must be entered by user
        )
    )
    dosage = 1


class StudentInterventionAttendanceEventFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    interventionReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            interventionIdentificationCode=None,  # Must be entered by user
        )
    )
    eventDate = RandomDateAttribute()
    attendanceEventCategoryDescriptor = build_descriptor(
        "AttendanceEventCategory", "In Attendance"
    )
    interventionDuration = 2


class StudentLanguageInstructionProgramAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    englishLearnerParticipation = False


class StudentLearningObjectiveFactory(APIFactory):
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    gradingPeriodReference = factory.Dict(
        dict(
            gradingPeriodDescriptor=build_descriptor(
                "GradingPeriod", "First Six Weeks"
            ),
            periodSequence=None,  # Must be entered by user
            schoolId=SchoolClient.shared_elementary_school_id(),
            schoolYear=2014,
        )
    )
    learningObjectiveReference = factory.Dict(
        dict(learningObjectiveId=None, namespace="uri://ed-fi.org")
    )
    competencyLevelDescriptor = build_descriptor("CompetencyLevel", "Proficient")


class StudentMigrantEducationProgramAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    priorityForServices = False
    lastQualifyingMove = formatted_date(6, 6)


class StudentNeglectedOrDelinquentProgramAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    servedOutsideOfRegularSession = False


class StudentProgramAttendanceEventFactory(APIFactory):
    eventDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    attendanceEventCategoryDescriptor = build_descriptor(
        "AttendanceEventCategory", "Excused Absence"
    )
    attendanceEventReason = "Sick"


class StudentSchoolFoodServiceProgramAssociationFactory(APIFactory):
    beginDate = RandomDateAttribute()
    educationOrganizationReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id()
        )
    )  # Prepopulated ed org
    programReference = factory.Dict(
        dict(
            educationOrganizationId=LocalEducationAgencyClient.shared_education_organization_id(),
            programTypeDescriptor=None,
            programName=None,
        )
    )  # Prepopulated program
    studentReference = factory.Dict(
        dict(studentUniqueId=None)
    )
    directCertification = True


class StudentAssessmentFactory(APIFactory):
    studentAssessmentIdentifier = UniqueIdAttribute()
    studentReference = factory.Dict(dict(studentUniqueId=None))  # Prepopulated student
    assessmentReference = factory.Dict(
        dict(
            assessmentIdentifier=None,
            namespace="uri://ed-fi.org/Assessment/Assessment.xml",
        )
    )
    administrationDate = (
        RandomDateAttribute()
    )  # Along with studentReference and assessmentReference, this is the PK
    administrationEnvironmentDescriptor = build_descriptor(
        "AdministrationEnvironment", "Testing Center"
    )
    administrationLanguageDescriptor = build_descriptor("Language", "eng")
    serialNumber = "0"
    whenAssessedGradeLevelDescriptor = build_descriptor("GradeLevel", "Sixth grade")
    performanceLevels = factory.List(
        [
            factory.Dict(
                dict(
                    assessmentReportingMethodDescriptor=build_descriptor(
                        "AssessmentReportingMethod", "Scale score"
                    ),
                    performanceLevelDescriptor=build_descriptor(
                        "PerformanceLevel", "Fail"
                    ),
                    performanceLevelMet=True,
                )
            ),
        ]
    )
    scoreResults = factory.List(
        [
            factory.Dict(
                dict(
                    assessmentReportingMethodDescriptor=build_descriptor(
                        "AssessmentReportingMethod", "Scale score"
                    ),
                    result="25",
                    resultDatatypeTypeDescriptor=build_descriptor(
                        "ResultDatatypeType", "Integer"
                    ),
                )
            )
        ]
    )
