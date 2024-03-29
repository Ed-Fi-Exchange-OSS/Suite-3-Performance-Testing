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
from typing import List
from locust import FastHttpUser

from edfi_performance_test.tasks.volume.ed_fi_volume_test_base import EdFiVolumeTestBase
from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.helpers.api_metadata import (
    get_model_version,
)
from edfi_performance_test.helpers.module_helper import (
   get_dir_modules,
)

import logging


logger = logging.getLogger()


class VolumeTestMixin(object):
    min_wait = 4000
    max_wait = 9000


class VolumeTestUser(FastHttpUser):

    test_list: List[str]
    is_initialized: bool = False
    volume_test_root_namespace: str = "edfi_performance_test.tasks.volume."

    def on_start(self):
        if VolumeTestUser.is_initialized:
            return

        EdFiAPIClient.client = self.client
        EdFiAPIClient.token = None

        # Import root pipeclean modules
        volume_tests_dir = os.path.dirname(__file__)
        tasks_submodules = get_dir_modules(volume_tests_dir, self.volume_test_root_namespace)

        # Import modules under version specific subfolders
        volume_test_sub_dir_list = [dir for dir in os.listdir(volume_tests_dir) if os.path.isdir(os.path.join(volume_tests_dir, dir))]
        for dir in volume_test_sub_dir_list:
            path = os.path.join(os.path.dirname(__file__), dir)
            namespace_prefix = self.volume_test_root_namespace + dir + "."
            if dir[-1].isnumeric() and int(dir[-1]) <= get_model_version(str(VolumeTestUser.host)):
                task_list = get_dir_modules(path, namespace_prefix)
                tasks_submodules.extend(task_list)

        for mod_name in tasks_submodules:
            importlib.import_module(mod_name)

        # Dynamically create VolumeTest locust classes for all scenarios
        for subclass in EdFiVolumeTestBase.__subclasses__():
            if (
                (not VolumeTestUser.test_list
                    or subclass.__name__ in VolumeTestUser.test_list)
                and not subclass.__subclasses__()  # include only top most subclass
                and not subclass.skip_all_scenarios()  # allows overrides to skip endpoints defined in base class
            ):
                self.tasks.append(subclass)

        VolumeTestUser.is_initialized = True
