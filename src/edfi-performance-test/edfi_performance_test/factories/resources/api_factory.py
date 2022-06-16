# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import factory


class APIFactory(factory.Factory):
    """
    Wraps `factory.Factory` to add JSON-specific methods, as well as
    make it easier to use in the absence of an ORM.
    """
    @classmethod
    def build_dict(cls, **kwargs):
        return factory.build(dict, FACTORY_CLASS=cls, **kwargs)

    @classmethod
    def build_json(cls, **kwargs):
        return json.dumps(cls.build_dict(**kwargs))
