# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from locust import task

from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase


class ParentVolumeTest(EdFiVolumeTestBase):
    @task
    def run_parent_scenarios(self):
        update_attribute_value = [
            {
                "firstName": "Lexi",
                "lastSurname": "Johnson",
                "otherNameTypeDescriptor": build_descriptor(
                    "OtherNameType", "Nickname"
                ),
            }
        ]
        self.run_scenario("parentOtherNames", update_attribute_value)
        self.run_scenario(
            "parentOtherNames",
            update_attribute_value,
            firstName="Alexis",
            lastSurname="Johnson",
            personalTitlePrefix="Mrs.",
            sexDescriptor=build_descriptor("Sex", "Female"),
            addresses__0__addressTypeDescriptor=build_descriptor("AddressType", "Home"),
            addresses__0__streetNumberName="456 Cedar Street",
            electronicMails__0__electronicMailAddress="alexisjohnson@email.com",
        )
