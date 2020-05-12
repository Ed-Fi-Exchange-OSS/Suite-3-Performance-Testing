from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.api.client.section import SectionClient


class GradebookEntryClient(EdFiAPIClient):
    endpoint = 'gradebookEntries'

    dependencies = {
        SectionClient: {},
    }

    def create_with_dependencies(self, **kwargs):
        section_reference = self.section_client.create_with_dependencies()
        section_attrs = section_reference['attributes']

        return self.create_using_dependencies(
            section_reference,
            sectionReference__sectionIdentifier=section_attrs['sectionIdentifier'],
            sectionReference__localCourseCode=section_attrs['courseOfferingReference']['localCourseCode'],
            sectionReference__schoolId=section_attrs['courseOfferingReference']['schoolId'],
            sectionReference__schoolYear=section_attrs['courseOfferingReference']['schoolYear'],
            sectionReference__sessionName=section_attrs['courseOfferingReference']['sessionName'],
        )
