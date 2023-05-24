# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import urllib.parse
from locust import task

from edfi_performance_test.api.client.graduation_plan import GraduationPlanClient
from edfi_performance_test.api.client.program import ProgramClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import formatted_date, RandomDateAttribute
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class StudentParentAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("primaryContactStatus", False)
        self.run_scenario(
            "emergencyContactStatus",
            False,
            relationDescriptor=build_descriptor("Relation", "Mother"),
        )


class StudentSchoolAssociationVolumeTest(EdFiVolumeTestBase):
    _graduation_year = None

    @task
    def run_association_scenarios(self):
        school_id = SchoolClient.shared_high_school_id()
        graduation_plan_reference = {  # Prepopulated graduation plan
            "educationOrganizationId": school_id,
            "graduationPlanTypeDescriptor": build_descriptor(
                "GraduationPlanType", "Recommended"
            ),
            "graduationSchoolYear": StudentSchoolAssociationVolumeTest.get_graduation_plan_school_year(
                self, school_id
            ),
        }
        self.run_scenario(
            "entryDate",
            RandomDateAttribute(),
            exitWithdrawDate=formatted_date(9, 1),
            exitWithdrawTypeDescriptor=build_descriptor(
                "ExitWithdrawType", "Transferred"
            ),
        )
        self.run_scenario(
            "graduationPlanReference",
            graduation_plan_reference,
            schoolReference__schoolId=school_id,
            entryGradeLevelDescriptor=build_descriptor("GradeLevel", "Ninth Grade"),
            classOfSchoolYearTypeReference__schoolYear=2020,
        )

    @classmethod
    def get_graduation_plan_school_year(cls, self, school_id):
        if cls._graduation_year is not None:
            return cls._graduation_year
        client_instance = GraduationPlanClient(
            self._api_client.client, token=self._api_client.token
        )
        plan_type = urllib.parse.quote_plus(
            build_descriptor("GraduationPlanType", "Recommended")
        )
        query = "?graduationPlanTypeDescriptor={}&educationOrganizationId={}".format(
            plan_type, school_id
        )
        all_graduation_years = client_instance.get_list(query)
        if all_graduation_years:
            cls._graduation_year = all_graduation_years[0][
                "graduationSchoolYearTypeReference"
            ]["schoolYear"]
        return cls._graduation_year


class StudentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_student_scenarios(self):
        self.run_scenario("telephoneNumber", '"111-222-4444')
        self.run_scenario(
            "cityStreetName",
            "123 Cedar Street",
            birthDate="1/1/2001",
            firstName="Madison",
            middleName="Mary",
            lastSurname="Johnson",
            sexDescriptor=build_descriptor("Sex", "Female"),
            birthCountryDescriptor=build_descriptor("Country", "US"),
            addresses__0__addressTypeDescriptor=build_descriptor("AddressType", "Home"),
            addresses__0__cityStreetName="123 Cedar",
            electronicMails__0__electronicMail="Madison@edficert.org",
            identificationCodes__0__identificationCode=705,
            languages=[],
            studentRaces__0__raceDescriptor=build_descriptor("Race", "White"),
            telephones=[],
        )

    def _update_attribute(
        self,
        resource_id,
        resource_attrs,
        update_attribute_name,
        update_attribute_value,
        **kwargs
    ):
        if update_attribute_name == "cityStreetName":
            # Update second student street name
            resource_attrs["addresses"][0][
                update_attribute_name
            ] = update_attribute_value
        else:  # Default (first) student; update first telephone number
            resource_attrs["telephones"][0][
                update_attribute_name
            ] = update_attribute_value
        self.update(resource_id, **resource_attrs)


class StudentEducationOrganizationAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario()
        self.run_scenario(
            studentCharacteristics__0__studentCharacteristicDescriptor=build_descriptor(
                "StudentCharacteristic", "Economic Disadvantaged"
            )
        )


class StudentCohortAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("endDate", formatted_date(9, 21))
        self.run_scenario(schoolId=SchoolClient.shared_high_school_id())


class StudentTitleIPartAProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario(
            "titleIPartAParticipantDescriptor",
            build_descriptor("TitleIPartAParticipant", "Public Schoolwide Program"),
        )
        self.run_scenario(
            "titleIPartAParticipantDescriptor",
            build_descriptor("TitleIPartAParticipant", "Was not served"),
            titleIPartAParticipantDescriptor=build_descriptor(
                "TitleIPartAParticipant", "Local Neglected Program"
            ),
        )


class StudentSpecialEducationProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("ideaEligibility", False)
        self.run_scenario(
            "ideaEligibility",
            False,
            specialEducationSettingDescriptor=build_descriptor(
                "SpecialEducationSetting",
                "Inside regular class less than 40% of the day",
            ),
        )


class StudentProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("endDate", formatted_date(9, 30))
        program_type = ProgramClient.shared_program_name()
        self.run_scenario(
            "endDate",
            formatted_date(10, 20),
            programReference__programTypeDescriptor=build_descriptor(
                "ProgramType", program_type
            ),
            programReference__programName=program_type,
        )


class StudentDisciplineIncidentAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario()
        self.run_scenario(schoolId=SchoolClient.shared_high_school_id())


class StudentSectionAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("endDate", formatted_date(12, 10))
        self.run_scenario(
            "endDate",
            formatted_date(12, 10),
            schoolId=SchoolClient.shared_high_school_id(),
            homeroomIndicator=True,
            courseCode="ALG-2",
        )


class StudentSchoolAttendanceEventVolumeTest(EdFiVolumeTestBase):
    @task
    def run_event_scenarios(self):
        self.run_scenario("attendanceEventReason", "Late")
        self.run_scenario(
            "attendanceEventReason",
            "No Note",
            schoolId=SchoolClient.shared_high_school_id(),
            eventDate=formatted_date(10, 5),
            attendanceEventCategoryDescriptor=build_descriptor(
                "AttendanceEventCategory", "Unexcused Absence"
            ),
        )


class StudentSectionAttendanceEventVolumeTest(EdFiVolumeTestBase):
    @task
    def run_event_scenarios(self):
        self.run_scenario("attendanceEventReason", "Late")
        self.run_scenario(
            "attendanceEventReason",
            "No Note",
            schoolId=SchoolClient.shared_high_school_id(),
            eventDate=formatted_date(10, 5),
            attendanceEventCategoryDescriptor=build_descriptor(
                "AttendanceEventCategory", "Unexcused Absence"
            ),
            courseCode="ALG-2",
        )


class StudentAcademicRecordVolumeTest(EdFiVolumeTestBase):
    @task
    def run_record_scenarios(self):
        self.run_scenario()
        self.run_scenario(
            "Credits",
            schoolId=SchoolClient.shared_high_school_id(),
            cumulativeAttemptedCredits=40,
            cumulativeEarnedCredits=38,
            sessionAttemptedCredits=3,
            sessionEarnedCredits=3,
        )

    def _update_attribute(
        self,
        resource_id,
        resource_attrs,
        update_attribute_name,
        update_attribute_value,
        **kwargs
    ):
        resource_attrs.update(
            dict(
                cumulativeAttemptedCredits=43,
                cumulativeEarnedCredits=41,
                sessionAttemptedCredits=6,
                sessionEarnedCredits=6,
            )
        )


class StudentCTEProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("programName", "Career and Technical Education")
        self.run_scenario(
            "endDate",
            formatted_date(12, 10)
        )


class StudentHomelessProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("programName", "Homeless")
        self.run_scenario(
            homelessPrimaryNighttimeResidenceDescriptor=build_descriptor(
                "HomelessPrimaryNighttimeResidence", "Doubled-up"
            ),
        )


class StudentLanguageInstructionProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("programName", "English as a Second Language (ESL)")
        self.run_scenario(
            priorityForServices=False,
        )


class StudentMigrantEducationProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("programName", "Migrant Education")
        self.run_scenario(
            "endDate",
            formatted_date(12, 10)
        )


class StudentNeglectedOrDelinquentProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("programName", "Neglected and Delinquent Program")
        self.run_scenario(
            neglectedOrDelinquentProgramServiceDescriptor=build_descriptor(
                "NeglectedOrDelinquentProgramService", "Dropout Prevention Programs"
            ),
        )


class StudentSchoolFoodServiceProgramAssociationVolumeTest(EdFiVolumeTestBase):
    @task
    def run_association_scenarios(self):
        self.run_scenario("programName", "School Food Service")
        self.run_scenario(
            schoolFoodServiceProgramServiceDescriptor=build_descriptor(
                "SchoolFoodServiceProgramService", "Free Lunch"
            ),
        )
