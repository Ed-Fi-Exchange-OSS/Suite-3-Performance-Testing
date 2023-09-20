# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient
from edfi_performance_test.api.client.school import SchoolClient


class StudentAssessmentEducationOrganizationAssociationClient(EdFiAPIClient):
    endpoint = "studentAssessmentEducationOrganizationAssociations"

    dependencies: Dict = {
        "edfi_performance_test.api.client.assessment.StudentAssessmentClient": {
            "client_name": "assessment_client",
        },
    }

    def create_with_dependencies(self, **kwargs):

        assessment_reference = self.assessment_client.create_with_dependencies()

        return self.create_using_dependencies(
            assessment_reference,
            educationOrganizationReference__educationOrganizationId=SchoolClient.shared_high_school_id(),
            studentAssessmentReference__assessmentIdentifier=assessment_reference[
                "attributes"
            ]["assessmentReference"]["assessmentIdentifier"],
            studentAssessmentReference__namespace=assessment_reference[
                "attributes"
            ]["assessmentReference"]["namespace"],
            studentAssessmentReference__studentAssessmentIdentifier=assessment_reference[
                "attributes"
            ]["studentAssessmentIdentifier"],
            studentAssessmentReference__studentUniqueId=assessment_reference[
                "attributes"
            ]["studentReference"]["studentUniqueId"],
            **kwargs
        )
