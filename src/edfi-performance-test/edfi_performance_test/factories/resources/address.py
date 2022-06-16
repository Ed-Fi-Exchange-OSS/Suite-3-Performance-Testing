# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..mixins import DefaultToDictMixin
from ..utils import RandomSuffixAttribute


class AddressFactory(DefaultToDictMixin, APIFactory):
    addressTypeDescriptor = build_descriptor('AddressType', 'Physical')
    city = RandomSuffixAttribute('Grand Oaks')
    postalCode = '73334'
    stateAbbreviationDescriptor = build_descriptor('StateAbbreviation', 'TX')
    streetNumberName = '456 Oaks Street'
