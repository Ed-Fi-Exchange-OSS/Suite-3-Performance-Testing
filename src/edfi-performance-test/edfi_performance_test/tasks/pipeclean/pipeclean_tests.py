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
import pkgutil
import edfi_performance_test.tasks.pipeclean

from locust import HttpUser

from edfi_performance_test.helpers.config import get_config_value
from edfi_performance_test.tasks.pipeclean.composite import EdFiCompositePipecleanTestBase
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
    EdFiPipecleanTaskSequence,
    EdFiPipecleanTestTerminator
)

class EdFiPipecleanTestMixin(object):
    min_wait = 2000
    max_wait = 9000


class DummyUser(HttpUser):
    tasks_submodules = [
        name
        for _, name, _ in pkgutil.iter_modules(
            [os.path.dirname(edfi_performance_test.tasks.pipeclean.__file__)],
            prefix="edfi_performance_test.tasks.pipeclean.",
        )
    ]

    for mod_name in tasks_submodules:
        importlib.import_module(mod_name)

    # Collect *PipecleanTest classes and append them to
    # EdFiPipecleanTaskSequence.tasks
    subclasses = EdFiPipecleanTestBase.__subclasses__()
    subclasses += EdFiCompositePipecleanTestBase.__subclasses__()
    subclasses.remove(EdFiCompositePipecleanTestBase)
    valid_names = set()
    # valid_names.add(AllDescriptorsPipecleanTest.__name__)
    for subclass in subclasses:
        name = subclass.__name__
        valid_names.add(name)
        EdFiPipecleanTaskSequence.tasks.append(subclass)
    # Add descriptor pipeclean tests after resource pipeclean tests
    # if it's been named or we're running everything
    # if len(args) == 0 or AllDescriptorsPipecleanTest.__name__ in args:
    #   EdFiPipecleanTaskSequence.tasks.append(AllDescriptorsPipecleanTest)

    EdFiPipecleanTaskSequence.tasks.append(EdFiPipecleanTestTerminator)

    #assign all pipeclean tasks to HttpUser
    tasks = {EdFiPipecleanTaskSequence}
