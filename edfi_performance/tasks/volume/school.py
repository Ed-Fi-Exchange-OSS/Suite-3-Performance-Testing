from locust import task

from edfi_performance.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance.factories.utils import random_chars
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class SchoolVolumeTest(EdFiVolumeTestBase):
    @task
    def run_school_scenarios(self):
        self.run_scenario('streetNumberName', '456 Cedar Street')
        ms_suffix = random_chars(4)
        self.run_scenario('telephoneNumber', '(950) 325-1231',
                          nameOfInstitution="Grand Oaks Middle School {}".format(ms_suffix),
                          shortNameOfInstitution="GOMS {}".format(ms_suffix),
                          addresses__0__streetNumberName="9993 West Blvd.",
                          gradeLevels=build_descriptor_dicts('GradeLevel',
                                                             ['Sixth grade', 'Seventh grade', 'Eighth grade']),
                          institutionTelephones=build_descriptor_dicts(
                              'InstitutionTelephoneNumberType',
                              [('Main', {'telephoneNumber': '(950) 325-9465'})]
                          ),
                          educationOrganizationCodes=build_descriptor_dicts(
                              'EducationOrganizationIdentificationSystem',
                              [('SEA', {'identificationCode': '255901444'})]))

    def _update_attribute(self, resource_id, resource_attrs, update_attribute_name, update_attribute_value, **kwargs):
        if update_attribute_name == 'telephoneNumber':
            # Update first institutionTelephones record
            resource_attrs['institutionTelephones'][0][update_attribute_name] = update_attribute_value
        else:  # Default (first) scenario; update first address streetNumberName
            resource_attrs['addresses'][0][update_attribute_name] = update_attribute_value
        self.update(resource_id, **resource_attrs)
