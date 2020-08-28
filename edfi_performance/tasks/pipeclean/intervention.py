# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import formatted_date
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class InterventionPrescriptionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'deliveryMethodDescriptor'
    update_attribute_value = build_descriptor('DeliveryMethod', 'Whole School')


class InterventionPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'beginDate'
    update_attribute_value = formatted_date(8, 24)


class InterventionStudyPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'participants'
    update_attribute_value = 30
