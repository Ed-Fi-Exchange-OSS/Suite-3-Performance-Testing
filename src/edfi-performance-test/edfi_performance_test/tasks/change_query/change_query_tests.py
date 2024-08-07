# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

"""
This module imports change query testing locusts for all scenarios
in the `tasks.change_query` and combines them into a single
locust which runs each scenario in order.
"""
import importlib
import os
import pkgutil
import edfi_performance_test.tasks.change_query

from locust import FastHttpUser
from typing import List

from edfi_performance_test.tasks.change_query.ed_fi_change_query_test_base import (
    EdFiChangeQueryTestBase,
    EdFiChangeQueryTaskSequence,
    EdFiChangeQueryTestTerminator,
)


class EdFiChangeQueryTestMixin(object):
    min_wait = 2000
    max_wait = 9000


class ChangeQueryTestUser(FastHttpUser):

    test_list: List[str]
    is_initialized: bool = False

    def on_start(self):
        if ChangeQueryTestUser.is_initialized:
            return

        tasks_submodules = [
            name
            for _, name, _ in pkgutil.iter_modules(
                [os.path.dirname(edfi_performance_test.tasks.change_query.__file__)],
                prefix="edfi_performance_test.tasks.change_query.",
            )
        ]

        for mod_name in tasks_submodules:
            importlib.import_module(mod_name)

        # Collect *ChangeQueryTest classes and append them to
        # EdFiChangeQueryTaskSequence.tasks
        for subclass in EdFiChangeQueryTestBase.__subclasses__():
            if (
                not ChangeQueryTestUser.test_list
                or subclass.__name__ in ChangeQueryTestUser.test_list
            ):
                EdFiChangeQueryTaskSequence.tasks.append(subclass)

        EdFiChangeQueryTaskSequence.tasks.append(EdFiChangeQueryTestTerminator)

        # assign all change query tasks to HttpUser
        self.tasks.append(EdFiChangeQueryTaskSequence)
        ChangeQueryTestUser.is_initialized = True
