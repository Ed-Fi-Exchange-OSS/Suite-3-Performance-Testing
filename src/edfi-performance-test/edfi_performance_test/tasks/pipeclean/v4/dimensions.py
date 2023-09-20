# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Any
from edfi_performance_test.api.client.ed_fi_api_client import import_from_dotted_path
from edfi_performance_test.factories.utils import random_chars
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import (
    EdFiPipecleanTestBase,
)


class DimensionPipecleanTestBase(EdFiPipecleanTestBase):
    def __init__(self, dimension: str, parent, *args, **kwargs):
        super(DimensionPipecleanTestBase, self).__init__(parent, *args, **kwargs)

        self.update_attribute_name = "codeName"
        self.update_attribute_value = random_chars(16)

        self._api_client.factory.namespace = f"uri://ed-fi.org/{dimension.title()}Dimension"
        self._api_client.endpoint = f"{dimension}Dimensions"

    def generate_client_class(self) -> Any:
        class_path = (
            self.__class__.__module__.replace("tasks.pipeclean", "api.client")
            + "."
            + "DimensionClient"
        )

        return import_from_dotted_path(class_path)


class BalanceSheetPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(BalanceSheetPipecleanTest, self).__init__(
            "balanceSheet", parent, *args, **kwargs
        )


class FunctionPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(FunctionPipecleanTest, self).__init__(
            "function", parent, *args, **kwargs
        )


class FundPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(FundPipecleanTest, self).__init__(
            "fund", parent, *args, **kwargs
        )


class ObjectPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ObjectPipecleanTest, self).__init__(
            "object", parent, *args, **kwargs
        )


class OperationalUnitPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(OperationalUnitPipecleanTest, self).__init__(
            "operationalUnit", parent, *args, **kwargs
        )


class ProgramPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProgramPipecleanTest, self).__init__(
            "program", parent, *args, **kwargs
        )


class ProjectPipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(ProjectPipecleanTest, self).__init__(
            "project", parent, *args, **kwargs
        )


class SourcePipecleanTest(DimensionPipecleanTestBase):
    def __init__(self, parent, *args, **kwargs):
        super(SourcePipecleanTest, self).__init__(
            "source", parent, *args, **kwargs
        )
