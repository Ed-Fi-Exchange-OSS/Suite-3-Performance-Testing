# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pkgutil
from typing import List


def get_dir_modules(path: str, namespace_prefix: str) -> List[str]:
    task_list = [
        name
        for _, name, _ in pkgutil.iter_modules(
            [path],
            prefix=namespace_prefix,
        )
    ]
    return task_list

def get_inheritors(classType) -> List:
    subclasses = []
    work = [classType]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.append(child)
                work.append(child)
    return subclasses
