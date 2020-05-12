import factory

from edfi_performance.api.client.student import StudentClient
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import ListOfDescriptors, build_descriptor
from edfi_performance.factories.resources.address import AddressFactory
from edfi_performance.factories.utils import UniquePrimaryKeyAttribute, RandomDateAttribute


class PostSecondaryInstitutionFactory(APIFactory):
    postSecondaryInstitutionId = UniquePrimaryKeyAttribute()
    nameOfInstitution = "University of Texas at Austin"
    addresses = factory.List([
        factory.SubFactory(AddressFactory),
    ])
    categories = ListOfDescriptors('EducationOrganizationCategory', ['Post Secondary Institution'])


class PostSecondaryEventFactory(APIFactory):
    eventDate = RandomDateAttribute()
    studentReference = factory.Dict(dict(studentUniqueId=StudentClient.shared_student_id()))
    postSecondaryEventCategoryDescriptor = build_descriptor('PostSecondaryEventCategory', 'College Acceptance')
    postSecondaryInstitutionReference = factory.Dict(dict(postSecondaryInstitutionId=None))  # Must be entered by user
