# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.mixins import DefaultToDictMixin
from edfi_performance_test.factories.utils import RandomSuffixAttribute


class AddressFactory(DefaultToDictMixin, APIFactory):
    addressTypeDescriptor = build_descriptor('AddressType', 'Physical')
    city = RandomSuffixAttribute('Grand Oaks')
    postalCode = '73334'
    stateAbbreviationDescriptor = build_descriptor('StateAbbreviation', 'TX')
    streetNumberName = '456 Oaks Street'
