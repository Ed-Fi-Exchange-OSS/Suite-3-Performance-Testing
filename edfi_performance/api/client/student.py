# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.assessment import LearningObjectiveClient
from edfi_performance.api.client.competency_objective import CompetencyObjectiveClient
from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.utils import RandomSuffixAttribute, formatted_date
from edfi_performance.api.client.parent import ParentClient


class StudentParentAssociationClient(EdFiAPIClient):
    endpoint = 'studentParentAssociations'

    dependencies = {
        'edfi_performance.api.client.student.StudentClient': {},
    }

    def create_with_dependencies(self, **kwargs):
        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies()

        # Create parent
        parent_unique_id = kwargs.pop('parentUniqueId', ParentClient.shared_parent_id())

        # Create parent - student association
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            parentReference__parentUniqueId=parent_unique_id,
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference,
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentClient(EdFiAPIClient):
    endpoint = 'students'

    _student_id = None

    dependencies = {
        'edfi_performance.api.client.student.StudentSchoolAssociationClient': {
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
        self.assoc_client.delete(reference['dependency_ids']['assoc_id'])
        self.delete(reference['resource_id'])

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
            schoolReference__schoolId=school_id,
        )
        assoc_overrides.update(kwargs)
        assoc_attrs = self.factory.build_dict(**assoc_overrides)
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])


class StudentEducationOrganizationAssociationClient(EdFiAPIClient):
    endpoint = 'studentEducationOrganizationAssociations'

    dependencies = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create ed org - student association
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentCohortAssociationClient(EdFiAPIClient):
    endpoint = 'studentCohortAssociations'

    dependencies = {
        'edfi_performance.api.client.cohort.CohortClient': {},
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
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            cohortReference__cohortIdentifier=cohort_reference['attributes']['cohortIdentifier'],
            cohortReference__educationOrganizationId=school_id,
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference,
                'cohort_reference': cohort_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.cohort_client.delete_with_dependencies(reference['dependency_ids']['cohort_reference'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentTitleIPartAProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentTitleIPartAProgramAssociations'

    dependencies = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student program association
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentSpecialEducationProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentSpecialEducationProgramAssociations'

    dependencies = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student program association
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentProgramAssociations'

    dependencies = {
        StudentClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student program association
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentDisciplineIncidentAssociationClient(EdFiAPIClient):
    endpoint = 'studentDisciplineIncidentAssociations'

    dependencies = {
        StudentClient: {},
        'edfi_performance.api.client.discipline.DisciplineIncidentClient': {
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
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            disciplineIncidentReference__schoolId=school_id,
            disciplineIncidentReference__incidentIdentifier=incident_reference['attributes']['incidentIdentifier'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference,
                'incident_reference': incident_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.incident_client.delete_with_dependencies(reference['dependency_ids']['incident_reference'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentSectionAssociationClient(EdFiAPIClient):
    endpoint = 'studentSectionAssociations'

    dependencies = {
        'edfi_performance.api.client.section.SectionClient': {},
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
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_unique_id,
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'attributes': assoc_attrs,
            'dependency_ids': {
                'student_reference': student_reference,
                'section_reference': section_reference,
            }
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        dependencies = reference['dependency_ids']
        self.student_client.delete_with_dependencies(dependencies['student_reference'])
        self.section_client.delete_with_dependencies(dependencies['section_reference'])


class StudentSchoolAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentSchoolAttendanceEvents'

    dependencies = {
        StudentClient: {},
        'edfi_performance.api.client.session.SessionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create session
        session_reference = self.session_client.create_with_dependencies(schoolId=school_id)

        # Create student school attendance event
        event_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            sessionReference__sessionName=session_reference['attributes']['sessionName'],
            schoolReference__schoolId=school_id,
            sessionReference__schoolId=school_id,
            **kwargs
        )
        event_id = self.create(**event_attrs)

        return {
            'resource_id': event_id,
            'dependency_ids': {
                'student_reference': student_reference,
                'session_reference': session_reference
            },
            'attributes': event_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.session_client.delete_with_dependencies(reference['dependency_ids']['session_reference'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentSectionAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentSectionAttendanceEvents'

    dependencies = {
        'edfi_performance.api.client.section.SectionClient': {},
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
        event_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
            **kwargs
        )
        event_id = self.create(**event_attrs)

        return {
            'resource_id': event_id,
            'dependency_ids': {
                'student_reference': student_reference,
                'section_reference': section_reference,
            },
            'attributes': event_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.section_client.delete_with_dependencies(reference['dependency_ids']['section_reference'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentAcademicRecordClient(EdFiAPIClient):
    endpoint = 'studentAcademicRecords'

    dependencies = {
        StudentClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        school_id = kwargs.pop('schoolId', SchoolClient.shared_elementary_school_id())

        # Create enrolled student
        student_reference = self.student_client.create_with_dependencies(schoolId=school_id)

        # Create student academic record
        assoc_attrs = self.factory.build_dict(
            studentReference__studentUniqueId=student_reference['attributes']['studentUniqueId'],
            educationOrganizationReference__educationOrganizationId=school_id,
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'student_reference': student_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.student_client.delete_with_dependencies(reference['dependency_ids']['student_reference'])


class StudentCompetencyObjectiveClient(EdFiAPIClient):
    endpoint = 'studentCompetencyObjectives'

    dependencies = {
        'edfi_performance.api.client.grading_period.GradingPeriodClient': {},
        CompetencyObjectiveClient: {}
    }

    def create_with_dependencies(self, **kwargs):
        # Create grading period
        period_reference = self.grading_period_client.create_with_dependencies()

        # Create competency objective
        objective_reference = self.competency_objective_client.create_with_dependencies()

        # Create student competency objective
        student_objective_attrs = self.factory.build_dict(
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
            objectiveCompetencyObjectiveReference__objective=objective_reference['attributes']['objective']
        )
        student_objective_id = self.create(**student_objective_attrs)

        return {
            'resource_id': student_objective_id,
            'dependency_ids': {
                'objective_reference': objective_reference,
                'period_reference': period_reference
            },
            'attributes': student_objective_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.competency_objective_client.delete_with_dependencies(reference['dependency_ids']['objective_reference'])
        self.grading_period_client.delete_with_dependencies(reference['dependency_ids']['period_reference'])


class StudentCTEProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentCTEProgramAssociations'


class StudentEducationOrganizationResponsibilityAssociationClient(EdFiAPIClient):
    endpoint = 'studentEducationOrganizationResponsibilityAssociations'


class StudentGradebookEntryClient(EdFiAPIClient):
    endpoint = 'studentGradebookEntries'

    dependencies = {
        StudentSectionAssociationClient: {
            'client_name': 'assoc_client'
        },
        'edfi_performance.api.client.gradebook_entries.GradebookEntryClient': {
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

        student_entry_attrs = self.factory.build_dict(
            gradebookEntryReference=entry_attrs,
            studentSectionAssociationReference=assoc_attrs
        )
        student_entry_id = self.create(**student_entry_attrs)

        return {
            'resource_id': student_entry_id,
            'attributes': student_entry_attrs,
            'dependency_ids': {
                'entry_id': entry_id,
                'student_section_reference': student_section_reference
            }
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        dependencies = reference['dependency_ids']
        self.entry_client.delete(dependencies['entry_id'])
        self.assoc_client.delete_with_dependencies(dependencies['student_section_reference'])


class StudentHomelessProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentHomelessProgramAssociations'


class StudentInterventionAssociationClient(EdFiAPIClient):
    endpoint = 'studentInterventionAssociations'

    dependencies = {
        'edfi_performance.api.client.intervention.InterventionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        intervention_reference = self.intervention_client.create_with_dependencies()

        assoc_attrs = self.factory.build_dict(
            interventionReference__interventionIdentificationCode=intervention_reference['attributes']['interventionIdentificationCode'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'intervention_reference': intervention_reference,
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.intervention_client.delete_with_dependencies(reference['dependency_ids']['intervention_reference'])


class StudentInterventionAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentInterventionAttendanceEvents'

    dependencies = {
        'edfi_performance.api.client.intervention.InterventionClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        intervention_reference = self.intervention_client.create_with_dependencies()

        event_attrs = self.factory.build_dict(
            interventionReference__interventionIdentificationCode=intervention_reference['attributes']['interventionIdentificationCode'],
            **kwargs
        )
        event_id = self.create(**event_attrs)

        return {
            'resource_id': event_id,
            'dependency_ids': {
                'intervention_reference': intervention_reference,
            },
            'attributes': event_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.intervention_client.delete_with_dependencies(reference['dependency_ids']['intervention_reference'])


class StudentLanguageInstructionProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentLanguageInstructionProgramAssociations'


class StudentLearningObjectiveClient(EdFiAPIClient):
    endpoint = 'studentLearningObjectives'

    dependencies = {
        LearningObjectiveClient: {
            'client_name': 'objective_client'
        },
        'edfi_performance.api.client.grading_period.GradingPeriodClient': {}
    }

    def create_with_dependencies(self, **kwargs):
        objective_reference = self.objective_client.create_with_dependencies()

        period_reference = self.grading_period_client.create_with_dependencies()

        student_objective_attrs = self.factory.build_dict(
            learningObjectiveReference__objective=objective_reference['attributes']['objective'],
            gradingPeriodReference__periodSequence=period_reference['attributes']['periodSequence'],
            **kwargs
        )
        student_objective_id = self.create(**student_objective_attrs)

        return {
            'resource_id': student_objective_id,
            'dependency_ids': {
                'objective_reference': objective_reference,
                'period_reference': period_reference
            },
            'attributes': student_objective_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.objective_client.delete_with_dependencies(reference['dependency_ids']['objective_reference'])
        self.grading_period_client.delete_with_dependencies(reference['dependency_ids']['period_reference'])


class StudentMigrantEducationProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentMigrantEducationProgramAssociations'


class StudentNeglectedOrDelinquentProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentNeglectedOrDelinquentProgramAssociations'


class StudentProgramAttendanceEventClient(EdFiAPIClient):
    endpoint = 'studentProgramAttendanceEvents'


class StudentSchoolFoodServiceProgramAssociationClient(EdFiAPIClient):
    endpoint = 'studentSchoolFoodServiceProgramAssociations'
