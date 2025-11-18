# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

import importlib
import os
from typing import List

from locust import FastHttpUser

from edfi_performance_test.tasks.batch_volume.batch_volume_test_base import (
    BatchVolumeTestBase,
)
from edfi_performance_test.tasks.batch_volume.batch_volume_fixtures import (
    get_or_create_shared_school,
    get_or_create_shared_course_offering,
    get_or_create_shared_class_period,
    get_or_create_shared_location,
)
from edfi_performance_test.helpers.api_metadata import get_model_version
from edfi_performance_test.helpers.module_helper import get_dir_modules


class BatchVolumeTestUser(FastHttpUser):

    test_list: List[str]
    is_initialized: bool = False
    batch_volume_test_root_namespace: str = "edfi_performance_test.tasks.batch_volume."

    def on_start(self):
        if BatchVolumeTestUser.is_initialized:
            return

        # Lazily obtain an OAuth token for this user's HTTP client.
        from edfi_performance_test.api.client.ed_fi_basic_api_client import (
            EdFiBasicAPIClient,
        )
        from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient

        auth_client = EdFiBasicAPIClient(self.client)
        self.token = auth_client.token

        # Propagate the Locust HTTP client and token to EdFiAPIClient so that
        # existing clients can be used by fixture helpers.
        EdFiAPIClient.client = self.client
        EdFiAPIClient.token = self.token

        # Initialize shared fixtures once per test run so they can be
        # referenced by batch volume scenarios via their natural keys.
        get_or_create_shared_school()
        get_or_create_shared_course_offering()
        get_or_create_shared_class_period()
        get_or_create_shared_location()

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

        # Dynamically register all BatchVolumeTestBase subclasses as tasks.
        # By default, skip mixed-resource scenarios unless explicitly requested
        # via the test_list filter.
        for subclass in BatchVolumeTestBase.__subclasses__():
            if subclass.__subclasses__():
                continue

            if BatchVolumeTestUser.test_list:
                include = subclass.__name__ in BatchVolumeTestUser.test_list
            else:
                # When no explicit test list is provided, exclude the mixed
                # student/section scenario from the default batch volume run.
                include = subclass.__name__ != "MixedStudentSectionBatchVolumeTest"

            if include:
                self.tasks.append(subclass)

        BatchVolumeTestUser.is_initialized = True
