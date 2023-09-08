# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import Dict

from edfi_performance_test.api.client.ed_fi_api_client import EdFiAPIClient


class StudentGradebookEntryClientV4(EdFiAPIClient):
    endpoint = "studentGradebookEntries"

    dependencies: Dict = {
        "edfi_performance_test.api.client.v4.gradebook_entries.GradebookEntryClientV4": {
            "client_name": "entry_client",
        },
    }

    def create_with_dependencies(self, **kwargs):
        # Create new GradeBookEntry
        entry_reference = self.entry_client.create_with_dependencies()

        # Create student GradeBookEntry
        return self.create_using_dependencies(
            entry_reference,
            gradebookEntryReference__gradebookEntryIdentifier=entry_reference[
                "attributes"
            ]["gradebookEntryIdentifier"],
            gradebookEntryReference__namespace=entry_reference[
                "attributes"
            ]["namespace"],
            **kwargs
        )
