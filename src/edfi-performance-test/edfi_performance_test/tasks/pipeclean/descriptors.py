# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import traceback
from greenlet import GreenletExit
from requests.models import Response

import json

from locust import TaskSet, task
from locust.exception import StopUser, InterruptTaskSet

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.factories.utils import random_chars
from edfi_performance_test.helpers.config import get_config_value, DEFAULT_API_PREFIX


class DescriptorPipecleanTestBase(TaskSet):
    def __init__(self, descriptor, parent, *args, **kwargs):
        super(DescriptorPipecleanTestBase, self).__init__(parent, *args, **kwargs)
        descriptor_title = "{}{}".format(descriptor[0].upper(), descriptor[1:])
        self.namespace = "uri://ed-fi.org/{}Descriptor".format(descriptor_title)
        self.client = EdFiAPIClient.client
        self.token = EdFiAPIClient.token

        api_prefix: str = get_config_value("PERF_API_PREFIX", DEFAULT_API_PREFIX)
        self.list_endpoint = "{}/{}Descriptors".format(api_prefix, descriptor)

    @task
    def run_descriptor_pipeclean_test(self):
        try:
            self._touch_get_list_endpoint()
            resource_id = self._touch_post_endpoint()
            if self.is_invalid_response(resource_id):
                self._proceed_to_next_pipeclean_test()
            self._touch_get_detail_endpoint(resource_id)
            self._touch_put_endpoint(resource_id)
            self._touch_delete_endpoint(resource_id)
            self._proceed_to_next_pipeclean_test()
        except (StopUser, GreenletExit, InterruptTaskSet, KeyboardInterrupt):
            raise
        except Exception:
            traceback.print_exc()
            self._proceed_to_next_pipeclean_test()

    def detail_endpoint(self, resource_id):
        return "{}/{}".format(self.list_endpoint, resource_id)

    @property
    def detail_endpoint_name(self):
        return self.detail_endpoint("{id}")

    def get_headers(self):
        return {
            "Authorization": "Bearer {}".format(self.token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_payload(self):
        new_descriptor = random_chars(15)
        return dict(
            namespace=self.namespace,
            codeValue=new_descriptor,
            description=new_descriptor,
            shortDescription=new_descriptor,
        )

    def _touch_get_list_endpoint(self):
        return self.client.get(
            self.list_endpoint, headers=self.get_headers(), name=self.list_endpoint  # type:ignore
        )

    def _get_location(self, response: Response) -> str:
        if "location" not in response.headers:
            return ""

        return response.headers["location"].split("/")[-1].strip()

    def _touch_post_endpoint(self):
        response = self.client.post(
            self.list_endpoint,
            data=json.dumps(self.get_payload()),
            headers=self.get_headers(),
            name=self.list_endpoint,  # type: ignore
        )

        return self._get_location(response)

    def _touch_get_detail_endpoint(self, resource_id):
        return self.client.get(
            self.detail_endpoint(resource_id),
            headers=self.get_headers(),
            name=self.detail_endpoint_name,  # type: ignore
        )

    def _touch_put_endpoint(self, resource_id):
        response = self.client.put(
            self.detail_endpoint(resource_id),
            data=json.dumps(self.get_payload()),
            headers=self.get_headers(),
            name=self.detail_endpoint_name,  # type: ignore
        )
        new_id = self._get_location(response)
        assert new_id == resource_id
        return resource_id

    def _touch_delete_endpoint(self, resource_id):
        response = self.client.delete(
            self.detail_endpoint(resource_id),
            headers=self.get_headers(),
            name=self.detail_endpoint_name,  # type: ignore
        )
        return response == 204

    def _proceed_to_next_pipeclean_test(self):
        self.interrupt()

    @staticmethod
    def is_invalid_response(response):
        return response is None


class AbsenceEventCategoryDescriptorPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AbsenceEventCategoryDescriptorPipecleanTest, self).__init__(
            "absenceEventCategory", parent, *args, **kwargs
        )


class AcademicHonorCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AcademicHonorCategoryPipecleanTest, self).__init__(
            "academicHonorCategory", parent, *args, **kwargs
        )


class AcademicSubjectPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AcademicSubjectPipecleanTest, self).__init__(
            "academicSubject", parent, *args, **kwargs
        )


class AccommodationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AccommodationPipecleanTest, self).__init__(
            "accommodation", parent, *args, **kwargs
        )


class AccountClassificationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AccountClassificationPipecleanTest, self).__init__(
            "accountClassification", parent, *args, **kwargs
        )


class AchievementCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AchievementCategoryPipecleanTest, self).__init__(
            "achievementCategory", parent, *args, **kwargs
        )


class AdditionalCreditTypeyPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AdditionalCreditTypeyPipecleanTest, self).__init__(
            "additionalCreditType", parent, *args, **kwargs
        )


class AddressTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AddressTypePipecleanTest, self).__init__(
            "addressType", parent, *args, **kwargs
        )


class AdministrationEnvironmentPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AdministrationEnvironmentPipecleanTest, self).__init__(
            "administrationEnvironment", parent, *args, **kwargs
        )


class AdministrativeFundingControlPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AdministrativeFundingControlPipecleanTest, self).__init__(
            "administrativeFundingControl", parent, *args, **kwargs
        )


class AssessmentCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssessmentCategoryPipecleanTest, self).__init__(
            "assessmentCategory", parent, *args, **kwargs
        )


class AssessmentIdentificationSystemPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssessmentIdentificationSystemPipecleanTest, self).__init__(
            "assessmentIdentificationSystem", parent, *args, **kwargs
        )


class AssessmentItemCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssessmentItemCategoryPipecleanTest, self).__init__(
            "assessmentItemCategory", parent, *args, **kwargs
        )


class AssessmentItemResultPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssessmentItemResultPipecleanTest, self).__init__(
            "assessmentItemResult", parent, *args, **kwargs
        )


class AssessmentPeriodPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssessmentPeriodPipecleanTest, self).__init__(
            "assessmentPeriod", parent, *args, **kwargs
        )


class AssessmentReportingMethodPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AssessmentReportingMethodPipecleanTest, self).__init__(
            "assessmentReportingMethod", parent, *args, **kwargs
        )


class AttemptStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AttemptStatusPipecleanTest, self).__init__(
            "attemptStatus", parent, *args, **kwargs
        )


class AttendanceEventCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(AttendanceEventCategoryPipecleanTest, self).__init__(
            "attendanceEventCategory", parent, *args, **kwargs
        )


class BehaviorPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(BehaviorPipecleanTest, self).__init__("behavior", parent, *args, **kwargs)


class CalendarEventPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CalendarEventPipecleanTest, self).__init__(
            "calendarEvent", parent, *args, **kwargs
        )


class CalendarTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CalendarTypePipecleanTest, self).__init__(
            "calendarType", parent, *args, **kwargs
        )


class CareerPathwayPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CareerPathwayPipecleanTest, self).__init__(
            "careerPathway", parent, *args, **kwargs
        )


class CharterApprovalAgencyTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CharterApprovalAgencyTypePipecleanTest, self).__init__(
            "charterApprovalAgencyType", parent, *args, **kwargs
        )


class CharterStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CharterStatusPipecleanTest, self).__init__(
            "charterStatus", parent, *args, **kwargs
        )


class CitizenshipStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CitizenshipStatusPipecleanTest, self).__init__(
            "citizenshipStatus", parent, *args, **kwargs
        )


class ClassroomPositionPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ClassroomPositionPipecleanTest, self).__init__(
            "classroomPosition", parent, *args, **kwargs
        )


class CohortScopePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CohortScopePipecleanTest, self).__init__(
            "cohortScope", parent, *args, **kwargs
        )


class CohortTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CohortTypePipecleanTest, self).__init__(
            "cohortType", parent, *args, **kwargs
        )


class CohortYearTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CohortYearTypePipecleanTest, self).__init__(
            "cohortYearType", parent, *args, **kwargs
        )


class CompetencyLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CompetencyLevelPipecleanTest, self).__init__(
            "competencyLevel", parent, *args, **kwargs
        )


class ContactTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ContactTypePipecleanTest, self).__init__(
            "contactType", parent, *args, **kwargs
        )


class ContentClassPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ContentClassPipecleanTest, self).__init__(
            "contentClass", parent, *args, **kwargs
        )


class ContinuationOfServicesReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ContinuationOfServicesReasonPipecleanTest, self).__init__(
            "continuationOfServicesReason", parent, *args, **kwargs
        )


class CostRatePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CostRatePipecleanTest, self).__init__("costRate", parent, *args, **kwargs)


class CountryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CountryPipecleanTest, self).__init__("country", parent, *args, **kwargs)


class CourseAttemptResultPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CourseAttemptResultPipecleanTest, self).__init__(
            "courseAttemptResult", parent, *args, **kwargs
        )


class CourseDefinedByPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CourseDefinedByPipecleanTest, self).__init__(
            "courseDefinedBy", parent, *args, **kwargs
        )


class CourseGPAApplicabilityPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CourseGPAApplicabilityPipecleanTest, self).__init__(
            "courseGPAApplicability", parent, *args, **kwargs
        )


class CourseIdentificationSystemPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CourseIdentificationSystemPipecleanTest, self).__init__(
            "courseIdentificationSystem", parent, *args, **kwargs
        )


class CourseLevelCharacteristicPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CourseLevelCharacteristicPipecleanTest, self).__init__(
            "courseLevelCharacteristic", parent, *args, **kwargs
        )


class CourseRepeatCodePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CourseRepeatCodePipecleanTest, self).__init__(
            "courseRepeatCode", parent, *args, **kwargs
        )


class CredentialFieldPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CredentialFieldPipecleanTest, self).__init__(
            "credentialField", parent, *args, **kwargs
        )


class CredentialTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CredentialTypePipecleanTest, self).__init__(
            "credentialType", parent, *args, **kwargs
        )


class CreditTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CreditTypePipecleanTest, self).__init__(
            "creditType", parent, *args, **kwargs
        )


class CurriculumUsedPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(CurriculumUsedPipecleanTest, self).__init__(
            "curriculumUsed", parent, *args, **kwargs
        )


class DeliveryMethodPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DeliveryMethodPipecleanTest, self).__init__(
            "deliveryMethod", parent, *args, **kwargs
        )


class DiagnosisPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DiagnosisPipecleanTest, self).__init__(
            "diagnosis", parent, *args, **kwargs
        )


class DiplomaLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DiplomaLevelPipecleanTest, self).__init__(
            "diplomaLevel", parent, *args, **kwargs
        )


class DiplomaTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DiplomaTypePipecleanTest, self).__init__(
            "diplomaType", parent, *args, **kwargs
        )


class DisabilityPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DisabilityPipecleanTest, self).__init__(
            "disability", parent, *args, **kwargs
        )


class DisabilityDesignationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DisabilityDesignationPipecleanTest, self).__init__(
            "disabilityDesignation", parent, *args, **kwargs
        )


class DisabilityDeterminationSourceTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DisabilityDeterminationSourceTypePipecleanTest, self).__init__(
            "disabilityDeterminationSourceType", parent, *args, **kwargs
        )


class DisciplineActionLengthDifferenceReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DisciplineActionLengthDifferenceReasonPipecleanTest, self).__init__(
            "disciplineActionLengthDifferenceReason", parent, *args, **kwargs
        )


class DisciplinePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(DisciplinePipecleanTest, self).__init__(
            "discipline", parent, *args, **kwargs
        )


class EducationalEnvironmentPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EducationalEnvironmentPipecleanTest, self).__init__(
            "educationalEnvironment", parent, *args, **kwargs
        )


class EducationOrganizationCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EducationOrganizationCategoryPipecleanTest, self).__init__(
            "educationOrganizationCategory", parent, *args, **kwargs
        )


class EducationOrganizationIdentificationSystemPipecleanTest(
    DescriptorPipecleanTestBase
):
    def __init__(self, parent, *args, **kwargs):
        super(EducationOrganizationIdentificationSystemPipecleanTest, self).__init__(
            "educationOrganizationIdentificationSystem", parent, *args, **kwargs
        )


class EducationPlanPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EducationPlanPipecleanTest, self).__init__(
            "educationPlan", parent, *args, **kwargs
        )


class ElectronicMailTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ElectronicMailTypePipecleanTest, self).__init__(
            "electronicMailType", parent, *args, **kwargs
        )


class EmploymentStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EmploymentStatusPipecleanTest, self).__init__(
            "employmentStatus", parent, *args, **kwargs
        )


class EntryGradeLevelReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EntryGradeLevelReasonPipecleanTest, self).__init__(
            "entryGradeLevelReason", parent, *args, **kwargs
        )


class EntryTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EntryTypePipecleanTest, self).__init__(
            "entryType", parent, *args, **kwargs
        )


class EventCircumstancePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(EventCircumstancePipecleanTest, self).__init__(
            "eventCircumstance", parent, *args, **kwargs
        )


class ExitWithdrawTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ExitWithdrawTypePipecleanTest, self).__init__(
            "exitWithdrawType", parent, *args, **kwargs
        )


class GradebookEntryTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(GradebookEntryTypePipecleanTest, self).__init__(
            "gradebookEntryType", parent, *args, **kwargs
        )


class GradeLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(GradeLevelPipecleanTest, self).__init__(
            "gradeLevel", parent, *args, **kwargs
        )


class GradeTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(GradeTypePipecleanTest, self).__init__(
            "gradeType", parent, *args, **kwargs
        )


class GradingPeriodPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(GradingPeriodPipecleanTest, self).__init__(
            "gradingPeriod", parent, *args, **kwargs
        )


class GraduationPlanTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(GraduationPlanTypePipecleanTest, self).__init__(
            "graduationPlanType", parent, *args, **kwargs
        )


class GunFreeSchoolsActReportingStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(GunFreeSchoolsActReportingStatusPipecleanTest, self).__init__(
            "gunFreeSchoolsActReportingStatus", parent, *args, **kwargs
        )


class HomelessPrimaryNighttimeResidencePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(HomelessPrimaryNighttimeResidencePipecleanTest, self).__init__(
            "homelessPrimaryNighttimeResidence", parent, *args, **kwargs
        )


class HomelessProgramServicePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(HomelessProgramServicePipecleanTest, self).__init__(
            "homelessProgramService", parent, *args, **kwargs
        )


class IdentificationDocumentUsePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(IdentificationDocumentUsePipecleanTest, self).__init__(
            "identificationDocumentUse", parent, *args, **kwargs
        )


class IncidentLocationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(IncidentLocationPipecleanTest, self).__init__(
            "incidentLocation", parent, *args, **kwargs
        )


class InstitutionTelephoneNumberTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(InstitutionTelephoneNumberTypePipecleanTest, self).__init__(
            "institutionTelephoneNumberType", parent, *args, **kwargs
        )


class InteractivityStylePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(InteractivityStylePipecleanTest, self).__init__(
            "interactivityStyle", parent, *args, **kwargs
        )


class InternetAccessPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(InternetAccessPipecleanTest, self).__init__(
            "internetAccess", parent, *args, **kwargs
        )


class InterventionClassPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(InterventionClassPipecleanTest, self).__init__(
            "interventionClass", parent, *args, **kwargs
        )


class InterventionEffectivenessRatingPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(InterventionEffectivenessRatingPipecleanTest, self).__init__(
            "interventionEffectivenessRating", parent, *args, **kwargs
        )


class LanguagePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LanguagePipecleanTest, self).__init__("language", parent, *args, **kwargs)


class LanguageInstructionProgramServicePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LanguageInstructionProgramServicePipecleanTest, self).__init__(
            "languageInstructionProgramService", parent, *args, **kwargs
        )


class LanguageUsePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LanguageUsePipecleanTest, self).__init__(
            "languageUse", parent, *args, **kwargs
        )


class LearningStandardCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LearningStandardCategoryPipecleanTest, self).__init__(
            "learningStandardCategory", parent, *args, **kwargs
        )


class LevelOfEducationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LevelOfEducationPipecleanTest, self).__init__(
            "levelOfEducation", parent, *args, **kwargs
        )


class LicenseStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LicenseStatusPipecleanTest, self).__init__(
            "licenseStatus", parent, *args, **kwargs
        )


class LicenseTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LicenseTypePipecleanTest, self).__init__(
            "licenseType", parent, *args, **kwargs
        )


class LimitedEnglishProficiencyPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LimitedEnglishProficiencyPipecleanTest, self).__init__(
            "limitedEnglishProficiency", parent, *args, **kwargs
        )


class LocalePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LocalePipecleanTest, self).__init__("locale", parent, *args, **kwargs)


class LocalEducationAgencyCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(LocalEducationAgencyCategoryPipecleanTest, self).__init__(
            "localEducationAgencyCategory", parent, *args, **kwargs
        )


class MagnetSpecialProgramEmphasisSchoolPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(MagnetSpecialProgramEmphasisSchoolPipecleanTest, self).__init__(
            "magnetSpecialProgramEmphasisSchool", parent, *args, **kwargs
        )


class MediumOfInstructionPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(MediumOfInstructionPipecleanTest, self).__init__(
            "mediumOfInstruction", parent, *args, **kwargs
        )


class MethodCreditEarnedPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(MethodCreditEarnedPipecleanTest, self).__init__(
            "methodCreditEarned", parent, *args, **kwargs
        )


class MigrantEducationProgramServicePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(MigrantEducationProgramServicePipecleanTest, self).__init__(
            "migrantEducationProgramService", parent, *args, **kwargs
        )


class MonitoredPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(MonitoredPipecleanTest, self).__init__(
            "monitored", parent, *args, **kwargs
        )


class NeglectedOrDelinquentProgramPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(NeglectedOrDelinquentProgramPipecleanTest, self).__init__(
            "neglectedOrDelinquentProgram", parent, *args, **kwargs
        )


class NetworkPurposePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(NetworkPurposePipecleanTest, self).__init__(
            "networkPurpose", parent, *args, **kwargs
        )


class OldEthnicityPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(OldEthnicityPipecleanTest, self).__init__(
            "oldEthnicity", parent, *args, **kwargs
        )


class OperationalStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(OperationalStatusPipecleanTest, self).__init__(
            "operationalStatus", parent, *args, **kwargs
        )


class OtherNameTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(OtherNameTypePipecleanTest, self).__init__(
            "otherNameType", parent, *args, **kwargs
        )


class ParticipationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ParticipationPipecleanTest, self).__init__(
            "participation", parent, *args, **kwargs
        )


class PerformanceBaseConversionPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PerformanceBaseConversionPipecleanTest, self).__init__(
            "performanceBaseConversion", parent, *args, **kwargs
        )


class PerformanceLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PerformanceLevelPipecleanTest, self).__init__(
            "performanceLevel", parent, *args, **kwargs
        )


class PersonalInformationVerificationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PersonalInformationVerificationPipecleanTest, self).__init__(
            "personalInformationVerification", parent, *args, **kwargs
        )


class PopulationServedPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PopulationServedPipecleanTest, self).__init__(
            "populationServed", parent, *args, **kwargs
        )


class PostingResultPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PostingResultPipecleanTest, self).__init__(
            "postingResult", parent, *args, **kwargs
        )


class PostSecondaryEventCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PostSecondaryEventCategoryPipecleanTest, self).__init__(
            "postSecondaryEventCategory", parent, *args, **kwargs
        )


class PostSecondaryInstitutionLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PostSecondaryInstitutionLevelPipecleanTest, self).__init__(
            "postSecondaryInstitutionLevel", parent, *args, **kwargs
        )


class ProficiencyPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProficiencyPipecleanTest, self).__init__(
            "proficiency", parent, *args, **kwargs
        )


class ProgramAssignmentPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramAssignmentPipecleanTest, self).__init__(
            "programAssignment", parent, *args, **kwargs
        )


class ProgramCharacteristicPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramCharacteristicPipecleanTest, self).__init__(
            "programCharacteristic", parent, *args, **kwargs
        )


class ProgramSponsorPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramSponsorPipecleanTest, self).__init__(
            "programSponsor", parent, *args, **kwargs
        )


class ProgramTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramTypePipecleanTest, self).__init__(
            "programType", parent, *args, **kwargs
        )


class ProgressPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgressPipecleanTest, self).__init__("progress", parent, *args, **kwargs)


class ProgressLevelPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgressLevelPipecleanTest, self).__init__(
            "progressLevel", parent, *args, **kwargs
        )


class ProviderCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProviderCategoryPipecleanTest, self).__init__(
            "providerCategory", parent, *args, **kwargs
        )


class ProviderProfitabilityPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProviderProfitabilityPipecleanTest, self).__init__(
            "providerProfitability", parent, *args, **kwargs
        )


class ProviderStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProviderStatusPipecleanTest, self).__init__(
            "providerStatus", parent, *args, **kwargs
        )


class PublicationStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(PublicationStatusPipecleanTest, self).__init__(
            "publicationStatus", parent, *args, **kwargs
        )


class RacePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RacePipecleanTest, self).__init__("race", parent, *args, **kwargs)


class ReasonExitedPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ReasonExitedPipecleanTest, self).__init__(
            "reasonExited", parent, *args, **kwargs
        )


class ReasonNotTestedPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ReasonNotTestedPipecleanTest, self).__init__(
            "reasonNotTested", parent, *args, **kwargs
        )


class RecognitionTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RecognitionTypePipecleanTest, self).__init__(
            "recognitionType", parent, *args, **kwargs
        )


class RelationePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RelationePipecleanTest, self).__init__(
            "relation", parent, *args, **kwargs
        )


class RepeatIdentifierPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RepeatIdentifierPipecleanTest, self).__init__(
            "repeatIdentifier", parent, *args, **kwargs
        )


class ReporterDescriptionPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ReporterDescriptionPipecleanTest, self).__init__(
            "reporterDescription", parent, *args, **kwargs
        )


class ResidencyStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ResidencyStatusPipecleanTest, self).__init__(
            "residencyStatus", parent, *args, **kwargs
        )


class ResponseIndicatorPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ResponseIndicatorPipecleanTest, self).__init__(
            "responseIndicator", parent, *args, **kwargs
        )


class ResponsibilityPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ResponsibilityPipecleanTest, self).__init__(
            "responsibility", parent, *args, **kwargs
        )


class RestraintEventReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RestraintEventReasonPipecleanTest, self).__init__(
            "restraintEventReason", parent, *args, **kwargs
        )


class ResultDatatypeTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ResultDatatypeTypePipecleanTest, self).__init__(
            "resultDatatypeType", parent, *args, **kwargs
        )


class RetestIndicatorPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(RetestIndicatorPipecleanTest, self).__init__(
            "retestIndicator", parent, *args, **kwargs
        )


class SchoolCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SchoolCategoryPipecleanTest, self).__init__(
            "schoolCategory", parent, *args, **kwargs
        )


class SchoolChoiceImplementStatusPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SchoolChoiceImplementStatusPipecleanTest, self).__init__(
            "schoolChoiceImplementStatus", parent, *args, **kwargs
        )


class SchoolFoodServiceProgramServicePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SchoolFoodServiceProgramServicePipecleanTest, self).__init__(
            "schoolFoodServiceProgramService", parent, *args, **kwargs
        )


class SchoolTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SchoolTypePipecleanTest, self).__init__(
            "schoolType", parent, *args, **kwargs
        )


class SectionCharacteristicPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SectionCharacteristicPipecleanTest, self).__init__(
            "sectionCharacteristic", parent, *args, **kwargs
        )


class SeparationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SeparationPipecleanTest, self).__init__(
            "separation", parent, *args, **kwargs
        )


class SeparationReasonPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SeparationReasonPipecleanTest, self).__init__(
            "separationReason", parent, *args, **kwargs
        )


class ServicePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ServicePipecleanTest, self).__init__("service", parent, *args, **kwargs)


class SexPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SexPipecleanTest, self).__init__("sex", parent, *args, **kwargs)


class SpecialEducationProgramServicePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SpecialEducationProgramServicePipecleanTest, self).__init__(
            "specialEducationProgramService", parent, *args, **kwargs
        )


class SpecialEducationSettingPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SpecialEducationSettingPipecleanTest, self).__init__(
            "specialEducationSetting", parent, *args, **kwargs
        )


class StaffClassificationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StaffClassificationPipecleanTest, self).__init__(
            "staffClassification", parent, *args, **kwargs
        )


class StaffIdentificationSystemPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StaffIdentificationSystemPipecleanTest, self).__init__(
            "staffIdentificationSystem", parent, *args, **kwargs
        )


class StaffLeaveEventCategoryPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StaffLeaveEventCategoryPipecleanTest, self).__init__(
            "staffLeaveEventCategory", parent, *args, **kwargs
        )


class StateAbbreviationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StateAbbreviationPipecleanTest, self).__init__(
            "stateAbbreviation", parent, *args, **kwargs
        )


class StudentCharacteristicPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StudentCharacteristicPipecleanTest, self).__init__(
            "studentCharacteristic", parent, *args, **kwargs
        )


class StudentIdentificationSystemPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StudentIdentificationSystemPipecleanTest, self).__init__(
            "studentIdentificationSystem", parent, *args, **kwargs
        )


class StudentParticipationCodePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(StudentParticipationCodePipecleanTest, self).__init__(
            "studentParticipationCode", parent, *args, **kwargs
        )


class TeachingCredentialBasisPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TeachingCredentialBasisPipecleanTest, self).__init__(
            "teachingCredentialBasis", parent, *args, **kwargs
        )


class TeachingCredentialPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TeachingCredentialPipecleanTest, self).__init__(
            "teachingCredential", parent, *args, **kwargs
        )


class TechnicalSkillsAssessmentPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TechnicalSkillsAssessmentPipecleanTest, self).__init__(
            "technicalSkillsAssessment", parent, *args, **kwargs
        )


class TelephoneNumberTypePipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TelephoneNumberTypePipecleanTest, self).__init__(
            "telephoneNumberType", parent, *args, **kwargs
        )


class TermPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TermPipecleanTest, self).__init__("term", parent, *args, **kwargs)


class TitleIPartAParticipantPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TitleIPartAParticipantPipecleanTest, self).__init__(
            "titleIPartAParticipant", parent, *args, **kwargs
        )


class TitleIPartASchoolDesignationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TitleIPartASchoolDesignationPipecleanTest, self).__init__(
            "titleIPartASchoolDesignation", parent, *args, **kwargs
        )


class TribalAffiliationPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(TribalAffiliationPipecleanTest, self).__init__(
            "tribalAffiliation", parent, *args, **kwargs
        )


class VisaPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(VisaPipecleanTest, self).__init__("visa", parent, *args, **kwargs)


class WeaponPipecleanTest(DescriptorPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(WeaponPipecleanTest, self).__init__("weapon", parent, *args, **kwargs)
