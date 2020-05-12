from locust import task

from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.tasks.volume import EdFiVolumeTestBase


class ParentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_parent_scenarios(self):
        update_attribute_value = [{
                'firstName': "Lexi",
                'lastSurname': "Johnson",
                'otherNameTypeDescriptor': build_descriptor('OtherNameType', 'Nickname')
            }]
        self.run_scenario('parentOtherNames', update_attribute_value)
        self.run_scenario('parentOtherNames', update_attribute_value,
                          firstName="Alexis",
                          lastSurname="Johnson",
                          personalTitlePrefix="Mrs.",
                          sexDescriptor=build_descriptor('Sex', 'Female'),
                          addresses__0__addressTypeDescriptor=build_descriptor('AddressType', 'Home'),
                          addresses__0__streetNumberName="456 Cedar Street",
                          electronicMails__0__electronicMailAddress="alexisjohnson@email.com")
