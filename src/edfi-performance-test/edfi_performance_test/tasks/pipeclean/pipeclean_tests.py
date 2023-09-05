# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
This module imports pipeclean-testing locusts for all scenarios
in the `tasks.pipeclean` and combines them into a single
locust which runs each scenario in order.
"""
import importlib
import os
import logging

from typing import List
from locust import HttpUser

from edfi_performance_test.tasks.pipeclean.composite import (
    EdFiCompositePipecleanTestBase,
)
from edfi_performance_test.tasks.pipeclean.descriptors import (
    DescriptorPipecleanTestBase,
)
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
    EdFiPipecleanTaskSequence,
    EdFiPipecleanTestTerminator,
)
from edfi_performance_test.helpers.api_metadata import (
   get_model_version,
)
from edfi_performance_test.helpers.module_helper import (
   get_dir_modules,
)

logger = logging.getLogger(__name__)


class EdFiPipecleanTestMixin(object):
    min_wait = 2000
    max_wait = 9000


class PipeCleanTestUser(HttpUser):

    test_list: List[str]
    is_initialized: bool = False
    pipeclean_test_root_namespace: str = "edfi_performance_test.tasks.pipeclean."

    def on_start(self):
        if PipeCleanTestUser.is_initialized:
            return

        # Import root pipeclean modules
        pipe_clean_dir = os.path.dirname(__file__)
        tasks_submodules = get_dir_modules(pipe_clean_dir, self.pipeclean_test_root_namespace)

        # Import modules under version specific subfolders
        pipe_clean_sub_dir_list = [dir for dir in os.listdir(pipe_clean_dir) if os.path.isdir(os.path.join(pipe_clean_dir, dir))]
        for dir in pipe_clean_sub_dir_list:
            path = os.path.join(os.path.dirname(__file__), dir)
            namespace_prefix = self.pipeclean_test_root_namespace + dir + "."
            if dir[-1].isnumeric() and int(dir[-1]) <= get_model_version(str(PipeCleanTestUser.host)):
                task_list = get_dir_modules(path, namespace_prefix)
                tasks_submodules.extend(task_list)

        for mod_name in tasks_submodules:
            importlib.import_module(mod_name)

        # Collect *PipecleanTest classes and append them to
        # EdFiPipecleanTaskSequence.tasks
        for subclass in EdFiPipecleanTestBase.__subclasses__():
            if (
                subclass != EdFiCompositePipecleanTestBase
                and subclass != DescriptorPipecleanTestBase
                and not subclass.__subclasses__()  # include only top most subclass
                and not subclass.skip_all_scenarios()  # allows overrides to skip endpoints defined in base class
            ):
                EdFiPipecleanTaskSequence.tasks.append(subclass)

        # Add composite pipeclean tests
        if os.environ["PERF_DISABLE_COMPOSITES"].lower() != "true":
            for subclass in EdFiCompositePipecleanTestBase.__subclasses__():
                EdFiPipecleanTaskSequence.tasks.append(subclass)
        else:
            logger.info("Composites tests have been disabled")

        # Add descriptor pipeclean tests
        for descriptorSubclass in DescriptorPipecleanTestBase.__subclasses__():
            if not descriptorSubclass.__subclasses__() and not descriptorSubclass.skip_all_scenarios():
                EdFiPipecleanTaskSequence.tasks.append(descriptorSubclass)

        # If a list of tests were given, filter out the rest
        if PipeCleanTestUser.test_list:
            EdFiPipecleanTaskSequence.tasks = list(
                filter(
                    lambda x: (x.__name__ in PipeCleanTestUser.test_list),
                    EdFiPipecleanTaskSequence.tasks,
                )
            )

        EdFiPipecleanTaskSequence.tasks.append(EdFiPipecleanTestTerminator)

        # assign all pipeclean tasks to HttpUser
        self.tasks.append(EdFiPipecleanTaskSequence)

        PipeCleanTestUser.is_initialized = True
