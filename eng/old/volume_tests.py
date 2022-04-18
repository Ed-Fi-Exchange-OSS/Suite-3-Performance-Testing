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
import sys
from types import ModuleType

from locust import HttpLocust

from edfi_performance.config import get_config_value
from edfi_performance.tasks.volume import EdFiVolumeTestBase

# Import modules under tasks.volume package so *VolumeTest classes are registered
tasks_submodules = [
    name for _, name, _ in pkgutil.iter_modules(
        [os.path.join('edfi_performance', 'tasks', 'volume')],
        prefix='edfi_performance.tasks.volume.')
]
for mod_name in tasks_submodules:
    importlib.import_module(mod_name)


class VolumeTestMixin(object):
    host = get_config_value('host')
    min_wait = 2000
    max_wait = 9000


_module = ModuleType(__name__)

# Dynamically create VolumeTest locust classes for all scenarios
for subclass in EdFiVolumeTestBase.__subclasses__():
    name = subclass.__name__
    export = type(
        name,
        (VolumeTestMixin, HttpLocust),
        {'task_set': subclass}
    )
    setattr(_module, name, export)

sys.modules[__name__] = _module
