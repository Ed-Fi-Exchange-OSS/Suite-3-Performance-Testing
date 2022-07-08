# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import formatted_date, UniqueIdAttribute


class DisciplineActionFactory(APIFactory):
    disciplineActionIdentifier = UniqueIdAttribute(num_chars=20)
    disciplineDate = formatted_date(9, 20)
    disciplines = factory.List(
        [
            factory.Dict(
                dict(
                    disciplineDescriptor=build_descriptor(
                        "Discipline", "Out of School Suspension"
                    )
                )
            ),
        ]
    )
    studentReference = factory.Dict(
        dict(studentUniqueId=111111)
    )  # Default value for scenarios, but not in DB
    actualDisciplineActionLength = 2
    studentDisciplineIncidentAssociations = factory.List(
        [
            factory.Dict(
                dict(
                    studentDisciplineIncidentAssociationReference=factory.Dict(
                        dict(
                            incidentIdentifier=None,  # Must be entered by user
                            schoolId=SchoolClient.shared_elementary_school_id(),  # Prepopulated school
                            studentUniqueId=111111,  # Default value for scenarios, but not in DB
                        )
                    ),
                ),
            ),
        ]
    )
    responsibilitySchoolReference = factory.Dict(
        dict(schoolId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school


class DisciplineIncidentFactory(APIFactory):
    incidentDate = formatted_date(9, 25)
    incidentIdentifier = UniqueIdAttribute(num_chars=20)
    schoolReference = factory.Dict(
        dict(schoolId=SchoolClient.shared_elementary_school_id())
    )  # Prepopulated school
    staffReference = factory.Dict(dict(staffUniqueId=None))  # Must be entered by user
    behaviors = factory.List(
        [
            factory.Dict(
                dict(
                    behaviorDescriptor=build_descriptor(
                        "Behavior", "School Code of Conduct"
                    )
                ),
            )
        ]
    )
    incidentLocationDescriptor = build_descriptor("IncidentLocation", "School Bus")
    reporterDescriptionDescriptor = build_descriptor("ReporterDescription", "Staff")
    reporterName = "Villa, Mike"
