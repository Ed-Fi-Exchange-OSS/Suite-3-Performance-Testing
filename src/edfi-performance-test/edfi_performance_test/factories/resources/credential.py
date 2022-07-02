# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import factory

from edfi_performance_test.factories.resources.api_factory import APIFactory
from edfi_performance_test.factories.descriptors.utils import build_descriptor
from edfi_performance_test.factories.utils import UniqueIdAttribute, formatted_date


class CredentialFactory(APIFactory):
    credentialIdentifier = UniqueIdAttribute(num_chars=60)
    stateOfIssueStateAbbreviationDescriptor = build_descriptor('StateAbbreviation', 'TX')
    credentialFieldDescriptor = build_descriptor('CredentialField', 'Mathematics')
    credentialTypeDescriptor = build_descriptor('CredentialType', 'Registration')
    teachingCredentialDescriptor = build_descriptor('TeachingCredential', 'Paraprofessional')
    issuanceDate = formatted_date(7, 4)
    gradeLevels = factory.List([
        factory.Dict(
            dict(gradeLevelDescriptor=build_descriptor('GradeLevel', 'Sixth grade')),
        ),
    ])
    namespace = "uri://ed-fi.org"
