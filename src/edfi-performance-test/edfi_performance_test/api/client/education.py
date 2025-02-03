# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.helpers.perf_suite_error import PerfSuiteError

from edfi_performance_test.api.client.ed_fi_api_client import (
    EdFiAPIClient,
    import_from_dotted_path,
)
from edfi_performance_test.api.client.school import SchoolClient


class EducationContentClient(EdFiAPIClient):
    endpoint = "educationContents"


class EducationOrganizationInterventionPrescriptionAssociationClient(EdFiAPIClient):
    endpoint = "educationOrganizationInterventionPrescriptionAssociations"

    dependencies: Dict = {
        "edfi_performance_test.api.client.intervention.InterventionPrescriptionClient": {
            "client_name": "prescription_client",
        }
    }

    def create_with_dependencies(self, **kwargs):
        rx_reference = self.prescription_client.create_with_dependencies()
        if(rx_reference is None or rx_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            rx_reference,
            interventionPrescriptionReference__interventionPrescriptionIdentificationCode=rx_reference[
                "attributes"
            ][
                "interventionPrescriptionIdentificationCode"
            ],
        )


class EducationOrganizationNetworkClient(EdFiAPIClient):
    endpoint = "educationOrganizationNetworks"


class EducationOrganizationNetworkAssociationClient(EdFiAPIClient):
    endpoint = "educationOrganizationNetworkAssociations"

    dependencies: Dict = {
        EducationOrganizationNetworkClient: {
            "client_name": "network_client",
        }
    }

    def create_with_dependencies(self, **kwargs):
        network_reference = self.network_client.create_with_dependencies()
        if(network_reference is None or network_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            network_reference,
            educationOrganizationNetworkReference__educationOrganizationNetworkId=network_reference[
                "attributes"
            ][
                "educationOrganizationNetworkId"
            ],
            **kwargs
        )


class EducationOrganizationPeerAssociationClient(EdFiAPIClient):
    endpoint = "educationOrganizationPeerAssociations"

    dependencies: Dict = {
        "edfi_performance_test.api.client.school.SchoolClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        school_reference = self.school_client.create_with_dependencies()
        if(school_reference is None or school_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            school_reference,
            peerEducationOrganizationReference__educationOrganizationId=school_reference[
                "attributes"
            ][
                "schoolId"
            ],
            educationOrganizationReference__educationOrganizationId=SchoolClient.shared_high_school_id(),
            **kwargs
        )


class EducationServiceCenterClient(EdFiAPIClient):
    endpoint = "educationServiceCenters"


class LocalEducationAgencyClient(EdFiAPIClient):
    endpoint = "localEducationAgencies"

    _education_organization_id = None

    dependencies: Dict = {
        EducationServiceCenterClient: {
            "client_name": "service_center_client",
        },
    }

    def create_with_dependencies(self, **kwargs):
        service_center_reference = self.service_center_client.create_with_dependencies()
        if(service_center_reference is None or service_center_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            service_center_reference,
            educationServiceCenterReference__educationServiceCenterId=service_center_reference[
                "attributes"
            ][
                "educationServiceCenterId"
            ],
        )

    @classmethod
    def shared_education_organization_id(cls):
        if cls._education_organization_id is not None:
            return cls._education_organization_id
        client_class = import_from_dotted_path(
            "edfi_performance_test.api.client.education.LocalEducationAgencyClient"
        )
        client_instance = client_class(client_class.client, token=client_class.token)

        ed_orgs = client_instance.get_list()

        if ed_orgs is None or len(ed_orgs) == 0:
            raise PerfSuiteError("There no local education agencies. Please create one and then try this test again.")

        cls._education_organization_id = ed_orgs[0][
            "localEducationAgencyId"
        ]
        return cls._education_organization_id


class FeederSchoolAssociationClient(EdFiAPIClient):
    endpoint = "feederSchoolAssociations"

    dependencies: Dict = {
        "edfi_performance_test.api.client.school.SchoolClient": {},
    }

    def create_with_dependencies(self, **kwargs):
        feeder_school_reference = self.school_client.create_with_dependencies()
        if(feeder_school_reference is None or feeder_school_reference["resource_id"] is None):
            return

        return self.create_using_dependencies(
            feeder_school_reference,
            feederSchoolReference__schoolId=feeder_school_reference["attributes"][
                "schoolId"
            ],
            schoolReference__schoolId=SchoolClient.shared_elementary_school_id(),
        )


class StateEducationAgencyClient(EdFiAPIClient):
    endpoint = "stateEducationAgencies"
