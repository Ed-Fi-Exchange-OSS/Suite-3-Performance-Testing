from .. import APIFactory
from ..descriptors.utils import build_descriptor
from ..mixins import DefaultToDictMixin
from ..utils import RandomSuffixAttribute


class AddressFactory(DefaultToDictMixin, APIFactory):
    addressTypeDescriptor = build_descriptor('AddressType', 'Physical')
    city = RandomSuffixAttribute('Grand Oaks')
    postalCode = '73334'
    stateAbbreviationDescriptor = build_descriptor('StateAbbreviation', 'TX')
    streetNumberName = '456 Oaks Street'
