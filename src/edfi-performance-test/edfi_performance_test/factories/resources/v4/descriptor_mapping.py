# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.utils import RandomSuffixAttribute


class DescriptorMappingFactory(APIFactory):
    mappedNamespace = "uri://ed-fi.org/AcademicSubjectDescriptor"
    mappedValue = "Advanced Algebra"
    namespace = "uri://ed-fi.org/AcademicSubjectDescriptor"
    value = RandomSuffixAttribute("Algebra II", suffix_length=5)
