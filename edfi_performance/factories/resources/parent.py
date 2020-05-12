import factory

from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..resources.address import AddressFactory
from ..utils import UniqueIdAttribute


class ParentFactory(APIFactory):
    parentUniqueId = UniqueIdAttribute()
    firstName = "Michael"
    lastSurname = "Jones"
    personalTitlePrefix = "Mr."
    sexDescriptor = build_descriptor('Sex', 'Male')
    addresses = factory.List([
        factory.SubFactory(
            AddressFactory,
            addressTypeDescriptor=build_descriptor('AddressType', 'Temporary'),
            city="Grand Bend",
            postalCode="78834",
            streetNumberName="654 Mission Hills",
            apartmentRoomSuiteNumber="100",
            nameOfCounty="Williston",
        )
    ])
    electronicMails = factory.List([
        dict(
            electronicMailAddress="michaeljones@gmail.com",
            electronicMailTypeDescriptor=build_descriptor('ElectronicMailType', 'Home/Personal'),
        )
    ])
