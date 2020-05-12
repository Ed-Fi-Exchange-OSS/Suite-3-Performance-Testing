from edfi_performance.tasks.change_query import EdFiChangeQueryTestBase


class StaffChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = 'staffs'


class StaffSectionAssociationChangeQueryTest(EdFiChangeQueryTestBase):
    endpoint = 'staffSectionAssociations'
