# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.cohort import CohortClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.utils import RandomSuffixAttribute


class OpenStaffPositionClient(EdFiAPIClient):
    endpoint = 'openStaffPositions'


class StaffClient(EdFiAPIClient):
    endpoint = 'staffs'

    _staff_id = None

    dependencies: Dict = {
        'edfi_performance_test.api.client.staff.StaffEducationOrganizationAssignmentAssociationClient': {
            'client_name': 'assoc_client',
        },
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create staff
        staff_attrs = self.factory.build_dict(**kwargs)
        staff_unique_id = staff_attrs['staffUniqueId']
        staff_id = self.create(**staff_attrs)

        # Associate staff with existing school to allow updates
        assoc_id = self.assoc_client.create(
            staffReference__staffUniqueId=staff_unique_id,
            educationOrganizationReference__educationOrganizationId=school_id,
            staffUniqueId=staff_unique_id,
        )

        return {
            'resource_id': staff_id,
            'dependency_ids': {
                'assoc_id': assoc_id,
            },
            'attributes': staff_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.assoc_client.delete_item(reference['dependency_ids']['assoc_id'])
        self.delete_item(reference['resource_id'])

    @classmethod
    def shared_staff_id(cls):
        if cls._staff_id is not None:
            return cls._staff_id
        cls._staff_id = cls.create_shared_resource('staffUniqueId')
        return cls._staff_id


class StaffEducationOrganizationAssignmentAssociationClient(EdFiAPIClient):
    endpoint = 'staffEducationOrganizationAssignmentAssociations'

    def create_with_dependencies(self, **kwargs):
        # Create new staff for association
        staff_unique_id = kwargs.pop('staffUniqueId', StaffClient.shared_staff_id())

        # Create association from staff to ed org
        edorg_id = kwargs.pop('educationOrganizationId', SchoolClient.shared_elementary_school_id())
        assoc_overrides = dict(
            staffReference__staffUniqueId=staff_unique_id,
            educationOrganizationReference__educationOrganizationId=edorg_id,
        )
        assoc_overrides.update(kwargs)
        return self.create_using_dependencies(**assoc_overrides)


class StaffAbsenceEventClient(EdFiAPIClient):
    endpoint = 'staffAbsenceEvents'


class StaffCohortAssociationClient(EdFiAPIClient):
    endpoint = 'staffCohortAssociations'

    dependencies: Dict = {
        CohortClient: {},
        StaffClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create cohort
        cohort_reference = self.cohort_client.create_with_dependencies(
            educationOrganizationReference__educationOrganizationId=school_id,
        )

        # Create staff
        staff_reference = self.staff_client.create_with_dependencies(schoolId=school_id)

        # Create association between new staff and new cohort
        return self.create_using_dependencies(
            [{'cohort_client': cohort_reference}, {'staff_client': staff_reference}],
            staffReference__staffUniqueId=staff_reference['attributes']['staffUniqueId'],
            cohortReference__cohortIdentifier=cohort_reference['attributes']['cohortIdentifier'],
            cohortReference__educationOrganizationId=school_id,
            **kwargs
        )


class StaffEducationOrganizationContactAssociationClient(EdFiAPIClient):
    endpoint = 'staffEducationOrganizationContactAssociations'


class StaffEducationOrganizationEmploymentAssociationClient(EdFiAPIClient):
    endpoint = 'staffEducationOrganizationEmploymentAssociations'


class StaffLeaveClient(EdFiAPIClient):
    endpoint = 'staffLeaves'


class StaffProgramAssociationClient(EdFiAPIClient):
    endpoint = 'staffProgramAssociations'


class StaffSchoolAssociationClient(EdFiAPIClient):
    endpoint = 'staffSchoolAssociations'

    dependencies: Dict = {
        StaffClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create staff record
        staff_reference = self.staff_client.create_with_dependencies(schoolId=school_id)

        return self.create_using_dependencies(
            staff_reference,
            staffReference__staffUniqueId=staff_reference['attributes']['staffUniqueId'],
            schoolReference__schoolId=school_id,
            **kwargs
        )


class StaffSectionAssociationClient(EdFiAPIClient):
    endpoint = 'staffSectionAssociations'

    dependencies: Dict = {
        'edfi_performance_test.api.client.section.SectionClient': {},
        StaffClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        course_code = kwargs.pop('courseCode', "ELA-01")

        # Create section and staff
        section_reference = self.section_client.create_with_dependencies(
            schoolId=school_id,
            courseCode=course_code,
            sectionIdentifier=RandomSuffixAttribute(course_code + "2017RM555"))
        staff_reference = self.staff_client.create_with_dependencies(schoolId=school_id)

        # Create association between staff and section
        sec_attrs = section_reference['attributes']
        return self.create_using_dependencies(
            [{'section_client': section_reference}, {'staff_client': staff_reference}],
            staffReference__staffUniqueId=staff_reference['attributes']['staffUniqueId'],
            sectionReference__sectionIdentifier=sec_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=sec_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=sec_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=sec_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=sec_attrs['courseOfferingReference']['sessionName'],
        )
