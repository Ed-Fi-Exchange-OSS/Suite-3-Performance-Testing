import factory

from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import UniqueIdAttribute, formatted_date


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
