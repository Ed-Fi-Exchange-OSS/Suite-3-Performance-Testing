# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.assessment import LearningObjectiveClient
from edfi_performance_test.api.client.competency_objective import CompetencyObjectiveClient
from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.utils import RandomSuffixAttribute, formatted_date
from edfi_performance_test.api.client.parent import ParentClient


class StudentParentAssociationClient(EdFiAPIClient):
    endpoint = 'studentParentAssociations'

    dependencies: Dict = {
        'edfi_performance_test.api.client.student.StudentClient': {},
    }

    def create_with_dependencies(self, **kwargs):
        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies()

        # Create parent
        parent_unique_id = kwargs.pop('parentUniqueId', ParentClient.shared_parent_id())

        # Create parent - student association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            parentReference__parentUniqueId=parent_unique_id,
            **kwargs
        )


class StudentClient(EdFiAPIClient):
    endpoint = 'students'

    _student_id = None

    dependencies: Dict = {
        'edfi_performance_test.api.client.student.StudentSchoolAssociationClient': {
            'client_name': 'assoc_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create student
        student_attrs = self.factory.build_dict(**kwargs)
        student_unique_id = student_attrs['studentUniqueId']
        student_id = self.create(**student_attrs)

        # Associate student with existing school to allow updates
        assoc_id = self.assoc_client.create(
            studentReference__studentUniqueId=student_unique_id,
            schoolReference__schoolId=school_id,
            studentUniqueId=student_unique_id
        )

        return {
            'resource_id': student_id,
            'dependency_ids': {
                'assoc_id': assoc_id,
            },
            'attributes': student_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.assoc_client.delete_item(reference['dependency_ids']['assoc_id'])
        self.delete_item(reference['resource_id'])

    @classmethod
    def shared_student_id(cls):
        if cls._student_id is not None:
            return cls._student_id
        cls._student_id = cls.create_shared_resource('studentUniqueId')
        return cls._student_id


class StudentSchoolAssociationClient(EdFiAPIClient):
    endpoint = 'studentSchoolAssociations'

    def create_with_dependencies(self, **kwargs):
        # Create new student for association
        student_unique_id = kwargs.pop('studentUniqueId', StudentClient.shared_student_id())

        # Create association from student to school
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        assoc_overrides = dict(
            studentReference__studentUniqueId=student_unique_id,
            schoolReference__schoolId=school_id
        )
        assoc_overrides.update(kwargs)
        return self.create_using_dependencies(**assoc_overrides)


class StudentEducationOrganizationAssociationClient(EdFiAPIClient):
    endpoint = 'studentEducationOrganizationAssociations'

    dependencies: Dict = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create ed org - student association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )


class StudentCohortAssociationClient(EdFiAPIClient):
    endpoint = 'studentCohortAssociations'

    dependencies: Dict = {
        'edfi_performance_test.api.client.cohort.CohortClient': {},
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create a cohort
        cohort_reference = self.cohort_client.create_with_dependencies(
            educationOrganizationReference__educationOrganizationId=school_id
        )

        # Create the cohort - student association
        return self.create_using_dependencies(
            [{'cohort_client': cohort_reference}, {'student_client': student_reference}],
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            cohortReference__cohortIdentifier=cohort_reference['attributes']['cohortIdentifier'],
            cohortReference__educationOrganizationId=school_id,
            **kwargs
        )


class StudentTitleIPartAProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentTitleIPartAProgramAssociations'

    dependencies: Dict = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student program association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )


class StudentSpecialEducationProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentSpecialEducationProgramAssociations'

    dependencies: Dict = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student program association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )


class StudentProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentProgramAssociations'

    dependencies: Dict = {
        StudentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student program association
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )


class StudentDisciplineIncidentAssociationClient(EdFiAPIClient):
    endpoint = 'studentDisciplineIncidentAssociations'

    dependencies: Dict = {
        StudentClient: {},
        'edfi_performance_test.api.client.discipline.DisciplineIncidentClient': {
            'client_name': 'incident_client'
        }
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create discipline incident
        incident_reference = self.incident_client.create_with_dependencies(schoolId=school_id)

        # Create student incident association
        return self.create_using_dependencies(
            [{'incident_client': incident_reference}, {'student_client': student_reference}],
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            disciplineIncidentReference__schoolId=school_id,
            disciplineIncidentReference__incidentIdentifier=incident_reference['attributes']['incidentIdentifier'],
            **kwargs
        )


class StudentSectionAssociationClient(EdFiAPIClient):
    endpoint = 'studentSectionAssociations'

    dependencies: Dict = {
        'edfi_performance_test.api.client.section.SectionClient': {},
        StudentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.get('schoolId', SchoolClient.shared_elementary_school_id())
        course_code = kwargs.pop('courseCode', 'ELA-01')
        # Create section and student
        section_reference = self.section_client.create_with_dependencies(
            schoolId=school_id,
            courseCode=course_code,
            sectionIdentifier=RandomSuffixAttribute(course_code+"2017RM555")
        )
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)
        student_unique_id = student_reference['attributes']['studentUniqueId']

        # Create association between newly created section and student
        section_attrs = section_reference['attributes']
        return self.create_using_dependencies(
            [{'section_client': section_reference}, {'student_client': student_reference}],
            studentReference__studentUniqueId=student_unique_id,
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
            **kwargs
        )


class StudentSchoolAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentSchoolAttendanceEvents'

    dependencies: Dict = {
        StudentClient: {},
        'edfi_performance_test.api.client.session.SessionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create session
        session_reference = self.session_client.create_with_dependencies(schoolId=school_id)

        # Create student school attendance event
        return self.create_using_dependencies(
            [{'session_client': session_reference}, {'student_client': student_reference}],
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            sessionReference__sessionName=session_reference['attributes']['sessionName'],
            schoolReference__schoolId=school_id,
            sessionReference__schoolId=school_id,
            **kwargs
        )


class StudentSectionAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentSectionAttendanceEvents'

    dependencies: Dict = {
        'edfi_performance_test.api.client.section.SectionClient': {},
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())
        course_code = kwargs.pop('courseCode', 'ELA-01')

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create section
        section_reference = self.section_client.create_with_dependencies(
            schoolId=school_id,
            courseCode=course_code,
            sectionIdentifier=RandomSuffixAttribute(course_code + "2017RM555"))

        # Create student section attendance event
        section_attrs = section_reference['attributes']
        return self.create_using_dependencies(
            [{'section_client': section_reference}, {'student_client': student_reference}],
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
            **kwargs
        )


class StudentAcademicRecordClient(EdFiAPIClient):
    endpoint = 'studentAcademicRecords'

    dependencies: Dict = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student academic record
        return self.create_using_dependencies(
            student_reference,
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            educationOrganizationReference__educationOrganizationId=school_id,
            **kwargs
        )


class StudentCompetencyObjectiveClient(EdFiAPIClient):
    endpoint = 'studentCompetencyObjectives'

    dependencies: Dict = {
        'edfi_performance_test.api.client.grading_period.GradingPeriodClient': {},
        CompetencyObjectiveClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create grading period
        period_reference = self.grading_period_client.create_with_dependencies()

        # Create competency objective
        objective_reference = self.competency_objective_client.create_with_dependencies()

        # Create student competency objective
        return self.create_using_dependencies(
            [{'grading_period_client': period_reference}, {'competency_objective_client': objective_reference}],
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
            objectiveCompetencyObjectiveReference__objective=objective_reference['attributes']['objective']
        )


class StudentCTEProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentCTEProgramAssociations'


class StudentEducationOrganizationResponsibilityAssociationClient(EdFiAPIClient):
    endpoint = 'studentEducationOrganizationResponsibilityAssociations'


class StudentGradebookEntryClient(EdFiAPIClient):
    endpoint = 'studentGradebookEntries'

    dependencies: Dict = {
        StudentSectionAssociationClient: {
            'client_name': 'assoc_client'
        },
        'edfi_performance_test.api.client.gradebook_entries.GradebookEntryClient': {
            'client_name': 'entry_client',
        },
    }

    def create_with_dependencies(self, **kwargs):
        # Create a student and section
        student_section_reference = self.assoc_client.create_with_dependencies()
        section_kwargs = {
            'sectionIdentifier': student_section_reference['attributes']['sectionReference']['sectionIdentifier'],
            'localCourseCode': student_section_reference['attributes']['sectionReference']['localCourseCode'],
            'schoolId': student_section_reference['attributes']['sectionReference']['schoolId'],
            'schoolYear': student_section_reference['attributes']['sectionReference']['schoolYear'],
            'sessionName': student_section_reference['attributes']['sectionReference']['sessionName'],
        }

        # Create gradebook entry
        entry_id, gradebook_entry_title = self.entry_client.create(
            unique_id_field='gradebookEntryTitle',
            sectionReference=section_kwargs
        )

        # Create student gradebook entry
        entry_attrs = dict(
            gradebookEntryTitle=gradebook_entry_title,
            dateAssigned=formatted_date(2, 2),
            **section_kwargs
        )

        assoc_attrs = dict(
            studentUniqueId=student_section_reference['attributes']['studentReference']['studentUniqueId'],
            beginDate=formatted_date(8, 23),
            **section_kwargs
        )

        return self.create_using_dependencies(
            [{'assoc_client': student_section_reference}, {'entry_client': entry_id}],
            gradebookEntryReference=entry_attrs,
            studentSectionAssociationReference=assoc_attrs
        )

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete_item(reference['resource_id'])
        dependencies = reference['dependency_ids']
        self.entry_client.delete(dependencies['entry_client'])
        self.assoc_client.delete_with_dependencies(dependencies['assoc_client'])


class StudentHomelessProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentHomelessProgramAssociations'


class StudentInterventionAssociationClient(EdFiAPIClient):
    endpoint = 'studentInterventionAssociations'

    dependencies: Dict = {
        'edfi_performance_test.api.client.intervention.InterventionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        intervention_reference = self.intervention_client.create_with_dependencies()

        return self.create_using_dependencies(
            intervention_reference,
            interventionReference__interventionIdentificationCode=intervention_reference['attributes']['interventionIdentificationCode'],
            **kwargs
        )


class StudentInterventionAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentInterventionAttendanceEvents'

    dependencies: Dict = {
        'edfi_performance_test.api.client.intervention.InterventionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        intervention_reference = self.intervention_client.create_with_dependencies()

        return self.create_using_dependencies(
            intervention_reference,
            interventionReference__interventionIdentificationCode=intervention_reference['attributes']['interventionIdentificationCode'],
            **kwargs
        )


class StudentLanguageInstructionProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentLanguageInstructionProgramAssociations'


class StudentLearningObjectiveClient(EdFiAPIClient):
    endpoint = 'studentLearningObjectives'

    dependencies: Dict = {
        LearningObjectiveClient: {
            'client_name': 'objective_client'
        },
        'edfi_performance_test.api.client.grading_period.GradingPeriodClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        objective_reference = self.objective_client.create_with_dependencies()

        period_reference = self.grading_period_client.create_with_dependencies()

        return self.create_using_dependencies(
            [{'grading_period_client': period_reference}, {'objective_client': objective_reference}],
            learningObjectiveReference__learningObjectiveId=objective_reference['attributes']['learningObjectiveId'],
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
            **kwargs
        )


class StudentMigrantEducationProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentMigrantEducationProgramAssociations'


class StudentNeglectedOrDelinquentProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentNeglectedOrDelinquentProgramAssociations'


class StudentProgramAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentProgramAttendanceEvents'


class StudentSchoolFoodServiceProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentSchoolFoodServiceProgramAssociations'
