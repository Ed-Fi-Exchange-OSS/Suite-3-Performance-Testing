# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

""" import traceback
from greenlet import GreenletExit

import json

from locust import SequentialTaskSet, TaskSet, task
from locust.core import TaskSetMeta
from locust.exception import StopUser, InterruptTaskSet

from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import EdFiPipecleanTestBase
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.factories.utils import random_chars
from edfi_performance_test.tasks.pipeclean.pipeclean_tests import EdFiPipecleanTestTerminator

ALL_DESCRIPTORS = [
    'absenceEventCategory',
    'academicHonorCategory',
    'academicSubject',
    'accommodation',
    'accountClassification',
    'achievementCategory',
    'additionalCreditType',
    'addressType',
    'administrationEnvironment',
    'administrativeFundingControl',
    'assessmentCategory',
    'assessmentIdentificationSystem',
    'assessmentItemCategory',
    'assessmentItemResult',
    'assessmentPeriod',
    'assessmentReportingMethod',
    'attemptStatus',
    'attendanceEventCategory',
    'behavior',
    'calendarEvent',
    'calendarType',
    'careerPathway',
    'charterApprovalAgencyType',
    'charterStatus',
    'citizenshipStatus',
    'classroomPosition',
    'cohortScope',
    'cohortType',
    'cohortYearType',
    'competencyLevel',
    'contactType',
    'contentClass',
    'continuationOfServicesReason',
    'costRate',
    'country',
    'courseAttemptResult',
    'courseDefinedBy',
    'courseGPAApplicability',
    'courseIdentificationSystem',
    'courseLevelCharacteristic',
    'courseRepeatCode',
    'credentialField',
    'credentialType',
    'creditType',
    'curriculumUsed',
    'deliveryMethod',
    'diagnosis',
    'diplomaLevel',
    'diplomaType',
    'disability',
    'disabilityDesignation',
    'disabilityDeterminationSourceType',
    'disciplineActionLengthDifferenceReason',
    'discipline',
    'educationalEnvironment',
    'educationOrganizationCategory',
    'educationOrganizationIdentificationSystem',
    'educationPlan',
    'electronicMailType',
    'employmentStatus',
    'entryGradeLevelReason',
    'entryType',
    'eventCircumstance',
    'exitWithdrawType',
    'gradebookEntryType',
    'gradeLevel',
    'gradeType',
    'gradingPeriod',
    'graduationPlanType',
    'gunFreeSchoolsActReportingStatus',
    'homelessPrimaryNighttimeResidence',
    'homelessProgramService',
    'identificationDocumentUse',
    'incidentLocation',
    'institutionTelephoneNumberType',
    'interactivityStyle',
    'internetAccess',
    'interventionClass',
    'interventionEffectivenessRating',
    'language',
    'languageInstructionProgramService',
    'languageUse',
    'learningStandardCategory',
    'levelOfEducation',
    'licenseStatus',
    'licenseType',
    'limitedEnglishProficiency',
    'locale',
    'localEducationAgencyCategory',
    'magnetSpecialProgramEmphasisSchool',
    'mediumOfInstruction',
    'methodCreditEarned',
    'migrantEducationProgramService',
    'monitored',
    'neglectedOrDelinquentProgram',
    'neglectedOrDelinquentProgramService',
    'networkPurpose',
    'oldEthnicity',
    'operationalStatus',
    'otherNameType',
    'participation',
    'performanceBaseConversion',
    'performanceLevel',
    'personalInformationVerification',
    'populationServed',
    'postingResult',
    'postSecondaryEventCategory',
    'postSecondaryInstitutionLevel',
    'proficiency',
    'programAssignment',
    'programCharacteristic',
    'programSponsor',
    'programType',
    'progress',
    'progressLevel',
    'providerCategory',
    'providerProfitability',
    'providerStatus',
    'publicationStatus',
    'race',
    'reasonExited',
    'reasonNotTested',
    'recognitionType',
    'relation',
    'repeatIdentifier',
    'reporterDescription',
    'residencyStatus',
    'responseIndicator',
    'responsibility',
    'restraintEventReason',
    'resultDatatypeType',
    'retestIndicator',
    'schoolCategory',
    'schoolChoiceImplementStatus',
    'schoolFoodServiceProgramService',
    'schoolType',
    'sectionCharacteristic',
    'separation',
    'separationReason',
    'service',
    'sex',
    'specialEducationProgramService',
    'specialEducationSetting',
    'staffClassification',
    'staffIdentificationSystem',
    'staffLeaveEventCategory',
    'stateAbbreviation',
    'studentCharacteristic',
    'studentIdentificationSystem',
    'studentParticipationCode',
    'teachingCredentialBasis',
    'teachingCredential',
    'technicalSkillsAssessment',
    'telephoneNumberType',
    'term',
    'titleIPartAParticipant',
    'titleIPartASchoolDesignation',
    'tribalAffiliation',
    'visa',
    'weapon',
]


class _DescriptorPipecleanTask(TaskSet):
    client = None           # Set during class instantiation
    token = None            # Set during class instantiation
    list_endpoint = None    # Set during class instantiation
    namespace = None        # Set during class instantiation

    def on_start(self):
        # Suppress exceptions thrown in the Test Lab environment
        # when self-signed certificates are used.
        self.client.verify = False

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
        return '{}/{}'.format(self.list_endpoint, resource_id)

    @property
    def detail_endpoint_name(self):
        return self.detail_endpoint('{id}')

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
        return self.client.get(self.list_endpoint, headers=self.get_headers(), name=self.list_endpoint)

    def _touch_post_endpoint(self):
        response = self.client.post(
            self.list_endpoint,
            data=json.dumps(self.get_payload()),
            headers=self.get_headers(),
            name=self.list_endpoint)
        return response.headers['Location'].split('/')[-1].strip()

    def _touch_get_detail_endpoint(self, resource_id):
        return self.client.get(
            self.detail_endpoint(resource_id),
            headers=self.get_headers(),
            name=self.detail_endpoint_name)

    def _touch_put_endpoint(self, resource_id):
        response = self.client.put(
            self.detail_endpoint(resource_id),
            data=json.dumps(self.get_payload()),
            headers=self.get_headers(),
            name=self.detail_endpoint_name)
        new_id = response.headers['Location'].split('/')[-1].strip()
        assert new_id == resource_id
        return resource_id

    def _touch_delete_endpoint(self, resource_id):
        response = self.client.delete(
            self.detail_endpoint(resource_id),
            headers=self.get_headers(),
            name=self.detail_endpoint_name)
        return response == 204

    def _proceed_to_next_pipeclean_test(self):
        self.interrupt()

    @staticmethod
    def is_invalid_response(response):
        return response is None


class AllDescriptorsPipecleanTest(SequentialTaskSet):
    def __init__(self, parent, *args, **kwargs):
        super(AllDescriptorsPipecleanTest, self).__init__(parent, *args, **kwargs)
        _client = EdFiAPIClient(self.locust.host)
        for descriptor in sorted(ALL_DESCRIPTORS):
            descriptor_title = '{}{}'.format(descriptor[0].upper(), descriptor[1:])
            self.tasks.append(
                TaskSetMeta(
                    "{}PipecleanTest".format(descriptor_title),
                    (_DescriptorPipecleanTask,),
                    {
                        'list_endpoint': '{}/{}Descriptors'.format(_client.API_PREFIX, descriptor),
                        'namespace': "uri://ed-fi.org/{}Descriptor".format(descriptor_title),
                        'client': self.client,
                        'token': _client.token,
                    }
                )
            )
        # Quit locust after running all descriptors' tests
        self.tasks.append(EdFiPipecleanTestTerminator)
 """
