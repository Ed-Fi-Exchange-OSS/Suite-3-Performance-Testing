# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance.api.client import EdFiAPIClient, get_config_value


class EducationContentClient(EdFiAPIClient):
    endpoint = 'educationContents'


class EducationOrganizationInterventionPrescriptionAssociationClient(EdFiAPIClient):
    endpoint = 'educationOrganizationInterventionPrescriptionAssociations'

    dependencies = {
        'edfi_performance.api.client.intervention.InterventionPrescriptionClient': {
            'client_name': 'prescription_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        rx_reference = self.prescription_client.create_with_dependencies()

        assoc_attrs = self.factory.build_dict(
            interventionPrescriptionReference__interventionPrescriptionIdentificationCode=
            rx_reference['attributes']['interventionPrescriptionIdentificationCode'],
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'rx_reference': rx_reference,
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.prescription_client.delete_with_dependencies(reference['dependency_ids']['rx_reference'])


class EducationOrganizationNetworkClient(EdFiAPIClient):
    endpoint = 'educationOrganizationNetworks'


class EducationOrganizationNetworkAssociationClient(EdFiAPIClient):
    endpoint = 'educationOrganizationNetworkAssociations'

    dependencies = {
        EducationOrganizationNetworkClient: {
            'client_name': 'network_client',
        }
    }

    def create_with_dependencies(self, **kwargs):
        network_reference = self.network_client.create_with_dependencies()

        assoc_attrs = self.factory.build_dict(
            educationOrganizationNetworkReference__educationOrganizationNetworkId=
            network_reference['attributes']['educationOrganizationNetworkId'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'network_reference': network_reference,
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.network_client.delete_with_dependencies(reference['dependency_ids']['network_reference'])


class EducationOrganizationPeerAssociationClient(EdFiAPIClient):
    endpoint = 'educationOrganizationPeerAssociations'

    dependencies = {
        'edfi_performance.api.client.school.SchoolClient': {},
    }

    def create_with_dependencies(self, **kwargs):
        school_1_reference = self.school_client.create_with_dependencies()
        school_2_reference = self.school_client.create_with_dependencies()

        assoc_attrs = self.factory.build_dict(
            peerEducationOrganizationReference__educationOrganizationId=school_1_reference['attributes']['schoolId'],
            educationOrganizationReference__educationOrganizationId=school_2_reference['attributes']['schoolId'],
            **kwargs
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'school_1_reference': school_1_reference,
                'school_2_reference': school_2_reference,
            },
            'attributes': assoc_attrs
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.school_client.delete_with_dependencies(reference['dependency_ids']['school_1_reference'])
        self.school_client.delete_with_dependencies(reference['dependency_ids']['school_2_reference'])


class EducationServiceCenterClient(EdFiAPIClient):
    endpoint = 'educationServiceCenters'


class LocalEducationAgencyClient(EdFiAPIClient):
    endpoint = 'localEducationAgencies'

    _education_organization_id = None

    dependencies = {
        EducationServiceCenterClient: {
            'client_name': 'service_center_client',
        },
    }

    def create_with_dependencies(self, **kwargs):
        service_center_reference = self.service_center_client.create_with_dependencies()

        agency_attrs = self.factory.build_dict(
            educationServiceCenterReference__educationServiceCenterId=
            service_center_reference['attributes']['educationServiceCenterId'],
        )
        agency_id = self.create(**agency_attrs)

        return {
            'resource_id': agency_id,
            'dependency_ids': {
                'service_center_reference': service_center_reference,
            },
            'attributes': agency_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.service_center_client.delete_with_dependencies(reference['dependency_ids']['service_center_reference'])

    @classmethod
    def shared_education_organization_id(cls):
        if cls._education_organization_id is not None:
            return cls._education_organization_id
        client_instance = cls(get_config_value('host'), token=cls.token)
        cls._education_organization_id = client_instance.get_list()[0]['localEducationAgencyId']
        return cls._education_organization_id


class FeederSchoolAssociationClient(EdFiAPIClient):
    endpoint = 'feederSchoolAssociations'

    dependencies = {
        'edfi_performance.api.client.school.SchoolClient': {},
    }

    def create_with_dependencies(self, **kwargs):
        feeder_school_reference = self.school_client.create_with_dependencies()
        school_reference = self.school_client.create_with_dependencies()

        assoc_attrs = self.factory.build_dict(
            feederSchoolReference__schoolId=feeder_school_reference['attributes']['schoolId'],
            schoolReference__schoolId=school_reference['attributes']['schoolId'],
        )
        assoc_id = self.create(**assoc_attrs)

        return {
            'resource_id': assoc_id,
            'dependency_ids': {
                'feeder_school_reference': feeder_school_reference,
                'school_reference': school_reference
            },
            'attributes': assoc_attrs,
        }

    def delete_with_dependencies(self, reference, **kwargs):
        self.delete(reference['resource_id'])
        self.school_client.delete_with_dependencies(reference['dependency_ids']['feeder_school_reference'])
        self.school_client.delete_with_dependencies(reference['dependency_ids']['school_reference'])


class StateEducationAgencyClient(EdFiAPIClient):
    endpoint = 'stateEducationAgencies'
