# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.



class DefaultToDictMixin(object):
    """
    FactoryBoy's build-to-dict mechanism doesn't handle subfactories
    gracefully.

    Mix this class into any factory you want to use as a `factory.SubFactory`
    and generate dicts or JSON from.
    """
    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        if model_class is None:
            model_class = dict
        return super(DefaultToDictMixin, cls)._build(model_class, *args, **kwargs)
