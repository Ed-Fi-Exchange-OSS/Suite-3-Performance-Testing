# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.factories.descriptors.utils import build_descriptor_dicts
from edfi_performance_test.factories.utils import random_chars
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.helpers.config import get_config_value


class SchoolVolumeTest(EdFiVolumeTestBase):
    @task
    def run_school_scenarios(self):
        self.run_scenario("streetNumberName", "456 Cedar Street")
        ms_suffix = random_chars(4)
        self.run_scenario(
            "telephoneNumber",
            "(950) 325-1231",
            nameOfInstitution="Grand Oaks Middle School {}".format(ms_suffix),
            shortNameOfInstitution="GOMS {}".format(ms_suffix),
            addresses__0__streetNumberName="9993 West Blvd.",
            gradeLevels=build_descriptor_dicts(
                "GradeLevel", ["Sixth grade", "Seventh grade", "Eighth grade"]
            ),
            institutionTelephones=build_descriptor_dicts(
                "InstitutionTelephoneNumberType",
                [("Main", {"telephoneNumber": "(950) 325-9465"})],
            ),
            identificationCodes=build_descriptor_dicts(
                "EducationOrganizationIdentificationSystem",
                [("SEA", {"identificationCode": "255901444"})],
            ),
        )

    def _update_attribute(
        self,
        resource_id,
        resource_attrs,
        update_attribute_name,
        update_attribute_value,
        **kwargs
    ):

        if get_config_value("INCLUDE_ID_IN_BODY").lower() == "true":
            resource_attrs["id"] = resource_id

        if update_attribute_name == "telephoneNumber":
            # Update first institutionTelephones record
            resource_attrs["institutionTelephones"][0][
                update_attribute_name
            ] = update_attribute_value
        else:  # Default (first) scenario; update first address streetNumberName
            resource_attrs["addresses"][0][
                update_attribute_name
            ] = update_attribute_value
        self.update(resource_id, **resource_attrs)
