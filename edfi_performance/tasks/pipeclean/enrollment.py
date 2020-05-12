from edfi_performance.tasks.pipeclean.composite import EdFiCompositePipecleanTestBase
enrollment_composite_resources = ['localEducationAgencies', 'schools', 'sections', 'staffs', 'students']


class LocalEducationAgencyEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    def _run_pipeclean_scenario(self):
        self.run_get_only_pipeclean_scenario()


class SchoolEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources


class SectionEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources


class StaffEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources


class StudentEnrollmentCompositePipecleanTest(EdFiCompositePipecleanTestBase):
    composite_resources = enrollment_composite_resources
