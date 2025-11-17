# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

import logging
import importlib
import os
from typing import List

from locust import FastHttpUser

from edfi_performance_test.helpers.api_metadata import get_model_version
from edfi_performance_test.helpers.module_helper import get_dir_modules


logger = logging.getLogger()


class BatchVolumeTestMixin(object):
    min_wait = 4000
    max_wait = 9000


class BatchVolumeTestUser(FastHttpUser):

    test_list: List[str]
    is_initialized: bool = False
    batch_volume_test_root_namespace: str = "edfi_performance_test.tasks.batch_volume."

    def on_start(self):
        if BatchVolumeTestUser.is_initialized:
            return

        batch_volume_tests_dir = os.path.dirname(__file__)
        tasks_submodules = get_dir_modules(
            batch_volume_tests_dir, self.batch_volume_test_root_namespace
        )

        batch_volume_test_sub_dir_list = [
            dir
            for dir in os.listdir(batch_volume_tests_dir)
            if os.path.isdir(os.path.join(batch_volume_tests_dir, dir))
        ]
        for dir in batch_volume_test_sub_dir_list:
            path = os.path.join(os.path.dirname(__file__), dir)
            namespace_prefix = self.batch_volume_test_root_namespace + dir + "."
            if dir[-1].isnumeric() and int(dir[-1]) <= get_model_version(
                str(BatchVolumeTestUser.host)
            ):
                task_list = get_dir_modules(path, namespace_prefix)
                tasks_submodules.extend(task_list)

        for mod_name in tasks_submodules:
            importlib.import_module(mod_name)

        BatchVolumeTestUser.is_initialized = True

