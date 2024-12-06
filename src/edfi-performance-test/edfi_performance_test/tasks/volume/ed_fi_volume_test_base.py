# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task
from edfi_performance_test.tasks.ed_fi_task_set import EdFiTaskSet
from edfi_performance_test.helpers.config import get_config_value


class EdFiVolumeTestBase(EdFiTaskSet):

    @classmethod
    def skip_all_scenarios(cls):
        return False

    @task(2)
    def run_scenario(
        self, update_attribute_name=None, update_attribute_value=None, **kwargs
    ):
        # Create resource instance
        reference = self.create_with_dependencies(**kwargs)
        if reference is None:
            return

        resource_id = reference["resource_id"]
        resource_attrs = reference["attributes"]

        if self.is_invalid_response(resource_id):
            return

        # Update resource attribute
        if update_attribute_name is not None:
            self._update_attribute(
                resource_id,
                resource_attrs,
                update_attribute_name,
                update_attribute_value,
            )

        # Delete resource
        self.delete_from_reference(reference)

    def _update_attribute(
        self,
        resource_id,
        resource_attrs,
        update_attribute_name,
        update_attribute_value,
        **kwargs
    ):
        resource_attrs[update_attribute_name] = update_attribute_value
        self.update(resource_id, **resource_attrs)

    @task(1)
    def run_unsuccessful_scenario(self, **kwargs):
        if not eval(get_config_value("PERF_FAIL_DELIBERATELY")):
            return  # Skip this scenario if the config value is set to false
        # Create a bad POST request
        self._api_client.create(
            name=self._api_client.list_endpoint() + " [Deliberate Failure]", **kwargs
        )

    @task(1)
    def stop(self):
        # Interrupt the TaskSet and hand over execution control back to the parent TaskSet.
        # Without interruption, TaskSet will never stop executing its tasks and hand over
        # execution back to the parent.
        self.interrupt()
