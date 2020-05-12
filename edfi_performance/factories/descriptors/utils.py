import factory


def _snake_to_title(descriptor_type):
    # convert snake_case to TitleCase
    return ''.join(c.title() for c in descriptor_type.split('_'))


def _normalize_descriptor_type(descriptor_type):
    if '_' in descriptor_type:
        descriptor_type = _snake_to_title(descriptor_type)
    if not descriptor_type.endswith('Descriptor'):
        descriptor_type = '{}Descriptor'.format(descriptor_type)
    return descriptor_type


def _descriptor_type_to_dict_key(descriptor_type):
    dt = _normalize_descriptor_type(descriptor_type)
    return '{}{}'.format(dt[0].lower(), dt[1:])


def _descriptor_type_to_endpoint(descriptor_type):
    return '{}s'.format(_descriptor_type_to_dict_key(descriptor_type))


def build_descriptor(descriptor_type, value):
    _namespace = "uri://ed-fi.org/"
    descriptor_type = _normalize_descriptor_type(descriptor_type)
    return "{}{}#{}".format(_namespace, descriptor_type, value)


def _build_descriptor_dicts(descriptor_type, values):
    descriptor_type = _normalize_descriptor_type(descriptor_type)
    key = _descriptor_type_to_dict_key(descriptor_type)
    for str_or_iterable in values:
        if isinstance(str_or_iterable, basestring):
            value = str_or_iterable
            defaults = {}
        else:
            value = str_or_iterable[0]
            defaults = str_or_iterable[1]
        defaults.update({key: build_descriptor(descriptor_type, value)})
        yield defaults


def build_descriptor_dicts(descriptor_type, values):
    """
    A common pattern in Ed-Fi resources is to have a list of dicts of
    descriptors, something like

    ```json
    {
      ...
      "gradeLevels": [
         {
            "gradeLevelDescriptor": "uri://ed-fi.org/GradeLevelDescriptor#Ninth grade"
         },
         {
            "gradeLevelDescriptor": "uri://ed-fi.org/GradeLevelDescriptor#Tenth grade"
         }
      ]
      ...
    }
    ```

    This allows for a shorthand instantiation instead of writing them out.

    Usage:
    ```pycon
    >>> list(build_descriptor_dicts('GradeLevel', ['Ninth grade', 'Tenth grade']))
    [
        {'gradeLevelDescriptor': 'uri://ed-fi.org/GradeLevelDescriptor#Ninth grade'},
        {'gradeLevelDescriptor': 'uri://ed-fi.org/GradeLevelDescriptor#Tenth grade'}
    ]
    >>> list(build_descriptor_dicts('TelephoneNumber', [
    ...    ('Main', {'telephoneNumber': '(123) 456-7890'}),
    ...    ('Fax', {'telephoneNumber': '(123) 456-0987'}),
    ... ]))
    [
      {
        'telephoneNumber': '(123) 456-7890',
        'telephoneNumberDescriptor': 'uri://ed-fi.org/TelephoneNumberDescriptor#Main'
      },
      {
        'telephoneNumber': '(123) 456-0987',
        'telephoneNumberDescriptor': 'uri://ed-fi.org/TelephoneNumberDescriptor#Fax'
      }
    ]
    ```
    """
    return list(_build_descriptor_dicts(descriptor_type, values))


class ListOfDescriptors(factory.List):
    """
    Wrapper around `build_descriptor_dicts for use in `APIFactory` definitions
    when you need a list of dictionaries containing descriptors, each with
    optional other data:

    Usage:
    ```python
    class SchoolFactory(APIFactory):
        gradeLevels = ListOfDescriptors('GradeLevel', ['Ninth grade', 'Tenth grade'])
        institutionTelephones = ListOfDescriptors(
            'InstitutionTelephoneNumberType',
            [
                ('Main', {'telephoneNumber': '(123)-456-7890'}),
                ('Fax', {'telephoneNumber': '(123)-456-9870'}),
            ]
        )
    ```
    """
    def __init__(self, descriptor_type, values):
        super(ListOfDescriptors, self).__init__([
            factory.Dict(dct)
            for dct in _build_descriptor_dicts(descriptor_type, values)
        ])
