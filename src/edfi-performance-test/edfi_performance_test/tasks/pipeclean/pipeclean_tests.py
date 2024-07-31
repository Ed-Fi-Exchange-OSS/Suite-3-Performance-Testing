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
from locust import FastHttpUser

from edfi_performance_test.tasks.pipeclean.composite import (
    EdFiCompositePipecleanTestBase,
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
   get_inheritors,
)

logger = logging.getLogger(__name__)


class EdFiPipecleanTestMixin(object):
    min_wait = 2000
    max_wait = 9000


class PipeCleanTestUser(FastHttpUser):

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
        for subclass in get_inheritors(EdFiPipecleanTestBase):
            if (
                not subclass.__subclasses__()  # include only top most subclass
                and not subclass.skip_all_scenarios()  # allows overrides to skip endpoints defined in base class
                and not (issubclass(subclass, EdFiCompositePipecleanTestBase) and os.environ["PERF_DISABLE_COMPOSITES"].lower() == "true")  # skip composites based on the configuration
            ):
                EdFiPipecleanTaskSequence.tasks.append(subclass)

        if os.environ["PERF_DISABLE_COMPOSITES"].lower() == "true":
            logger.info("Composites tests have been disabled")

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
