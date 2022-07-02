# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import formatted_date
from edfi_performance_test.tasks.pipeclean.ed_fi_pipeclean_test_base import EdFiPipecleanTestBase


class EducationContentPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'description'
    update_attribute_value = "A collection of learning resources for all grade levels"


class EducationOrganizationInterventionPrescriptionAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'beginDate'
    update_attribute_value = formatted_date(4, 20)


class EducationOrganizationNetworkPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'networkPurposeDescriptor'
    update_attribute_value = build_descriptor('NetworkPurpose', 'Collective Procurement')


class EducationOrganizationNetworkAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'endDate'
    update_attribute_value = formatted_date(12, 30)


class EducationOrganizationPeerAssociationPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, default_attributes):
        # This resource has no non-FK data attributes, so we'll update one of those
        default_attributes['educationOrganizationReference']['educationOrganizationId'] = SchoolClient.shared_elementary_school_id()
        self.update(resource_id, **default_attributes)


class EducationServiceCenterPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nameOfInstitution'
    update_attribute_value = "Texas Educational Service Center"


class FeederSchoolAssociationPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'beginDate'
    update_attribute_value = formatted_date(7, 4)


class LocalEducationAgencyPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nameOfInstitution'
    update_attribute_value = "Local Education Agency #8675309"


class StateEducationAgencyPipecleanTest(EdFiPipecleanTestBase):
    update_attribute_name = 'nameOfInstitution'
    update_attribute_value = "TX State Education Agency"
