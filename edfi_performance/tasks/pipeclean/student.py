from edfi_performance.api.client.school import SchoolClient
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import formatted_date, RandomDateAttribute
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class StudentParentAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'primaryContactStatus'
    update_attribute_value = False


class StudentSchoolAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'entryDate'
    update_attribute_value = RandomDateAttribute()


class StudentPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, attrs):
        attrs['telephones'][0]['telephoneNumber'] = "111-222-4444"
        self.update(resource_id, **attrs)


class StudentEducationOrganizationAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'hispanicLatinoEthnicity'
    update_attribute_value = True


class StudentCohortAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = formatted_date(9, 21)


class StudentTitleIPartAProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'titleIPartAParticipantDescriptor'
    update_attribute_value = build_descriptor('TitleIPartAParticipant', 'Public Schoolwide Program')


class StudentSpecialEducationProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'ideaEligibility'
    update_attribute_value = False


class StudentProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = formatted_date(9, 30)


class StudentDisciplineIncidentAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'studentParticipationCodeDescriptor'
    update_attribute_value = build_descriptor('StudentParticipationCode', 'Victim')


class StudentSectionAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = formatted_date(12, 10)

    def get_create_with_dependencies_kwargs(self):
        return dict(schoolId=SchoolClient.shared_elementary_school_id())


class StudentSchoolAttendanceEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'attendanceEventReason'
    update_attribute_value = 'Late'


class StudentSectionAttendanceEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'attendanceEventReason'
    update_attribute_value = 'Late'


class StudentAcademicRecordPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'termDescriptor'
    update_attribute_value = build_descriptor('Term', 'Spring Semester')


class StudentCompetencyObjectivePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'competencyLevelDescriptor'
    update_attribute_value = build_descriptor('CompetencyLevel', 'Advanced')


class StudentCTEProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nonTraditionalGenderStatus'
    update_attribute_value = False


class StudentEducationOrganizationResponsibilityAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = formatted_date(9, 9)


class StudentGradebookEntryPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'numericGradeEarned'
    update_attribute_value = 90


class StudentHomelessProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'awaitingFosterCare'
    update_attribute_value = False


class StudentInterventionAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'dosage'
    update_attribute_value = 2


class StudentInterventionAttendanceEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'interventionDuration'
    update_attribute_value = 3


class StudentLanguageInstructionProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'englishLearnerParticipation'
    update_attribute_value = True


class StudentLearningObjectivePipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'competencyLevelDescriptor'
    update_attribute_value = build_descriptor('CompetencyLevel', 'Advanced')


class StudentMigrantEducationProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'priorityForServices'
    update_attribute_value = True


class StudentNeglectedOrDelinquentProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'servedOutsideOfRegularSession'
    update_attribute_value = True


class StudentProgramAttendanceEventPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'attendanceEventReason'
    update_attribute_value = "Dentist Appointment"


class StudentSchoolFoodServiceProgramAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'directCertification'
    update_attribute_value = False
