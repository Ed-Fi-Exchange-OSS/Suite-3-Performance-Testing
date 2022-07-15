# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
This module dynamically creates volume-testing locusts for all scenarios
registered in the `tasks.volume` package.  To get a list of all possible
individual testing scenarios, run `locust -f volume_test.py --list`.
"""
import importlib
import os
import pkgutil
from locust import HttpUser
import edfi_performance_test.tasks.volume
from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class VolumeTestMixin(object):
    min_wait = 2000
    max_wait = 9000


class VolumeTestUser(HttpUser):
    def on_start(self):
        EdFiAPIClient.client = self.client
        EdFiAPIClient.token = None

        # Import modules under tasks.volume package so *VolumeTest classes are registered

        tasks_submodules = [
            name
            for _, name, _ in pkgutil.iter_modules(
                [os.path.dirname(edfi_performance_test.tasks.volume.__file__)],
                prefix="edfi_performance_test.tasks.volume.",
            )
        ]

        for mod_name in tasks_submodules:
            importlib.import_module(mod_name)

        # Dynamically create VolumeTest locust classes for all scenarios
        for subclass in EdFiVolumeTestBase.__subclasses__():
            self.tasks.append(subclass)
