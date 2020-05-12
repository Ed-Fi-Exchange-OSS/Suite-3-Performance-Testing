from edfi_performance.tasks import EdFiTaskSet
from edfi_performance.config import get_config_value


class EdFiVolumeTestBase(EdFiTaskSet):

    def run_scenario(self, update_attribute_name=None, update_attribute_value=None, **kwargs):
        # Create resource instance
        reference = self.create_with_dependencies(**kwargs)
        resource_id = reference['resource_id']
        resource_attrs = reference['attributes']

        if self.is_invalid_response(resource_id):
            return

        # Update resource attribute
        if update_attribute_name is not None:
            self._update_attribute(resource_id, resource_attrs, update_attribute_name, update_attribute_value)

        # Delete resource
        self.delete_from_reference(reference)

    def _update_attribute(self, resource_id, resource_attrs, update_attribute_name, update_attribute_value, **kwargs):
        resource_attrs[update_attribute_name] = update_attribute_value
        self.update(resource_id, **resource_attrs)

    def run_unsuccessful_scenario(self, **kwargs):
        if get_config_value('fail_deliberately') == 'false':
            return  # Skip this scenario if the config value is set to false
        # Create a bad POST request
        self._api_client.create(name=self._api_client.list_endpoint()+' [Deliberate Failure]', **kwargs)
