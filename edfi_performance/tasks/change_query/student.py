from edfi_performance.tasks.change_query import EdFiChangeQueryTestBase


class StudentChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = 'students'


class StudentSectionAssociationChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = 'studentSectionAssociations'


class StudentSectionAttendanceEventChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = 'studentSectionAttendanceEvents'


class StudentEducationOrganizationAssociationChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = 'studentEducationOrganizationAssociations'
