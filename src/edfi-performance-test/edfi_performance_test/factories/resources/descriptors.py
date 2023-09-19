# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.utils import (
    random_chars,
    RandomSuffixAttribute,
)
from edfi_performance_test.factories.resources.api_factory import APIFactory


class DescriptorFactory(APIFactory):
    _newDescriptor = random_chars(15)
    codeValue = _newDescriptor
    description = RandomSuffixAttribute(_newDescriptor, suffix_length=5)
    shortDescription = _newDescriptor
    namespace = "uri://ed-fi.org/Descriptor"
