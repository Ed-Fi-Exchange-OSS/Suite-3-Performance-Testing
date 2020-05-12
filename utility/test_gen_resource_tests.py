from pytest import mark, fixture
import json

import generate_lib as Generator


class Test_parse_args(object):
    def test_lowercase(self):
        argv = ['-m', 'a', '-n', 'b', '-r', 'c']

        metadataUrl, namespace, resource = Generator.parse_args(argv, lambda: None)

        assert metadataUrl == 'a'
        assert namespace == 'b'
        assert resource == 'c'

    def test_uppercase(self):
        argv = ['-M', 'a', '-N', 'b', '-R', 'c']

        metadataUrl, namespace, resource = Generator.parse_args(argv, lambda: None)

        assert not metadataUrl
        assert not namespace
        assert not resource

    def test_long_names(self):
        argv = ['--metadataUrl', 'a', '--namespace', 'b', '--resource', 'c']

        metadataUrl, namespace, resource = Generator.parse_args(argv, lambda: None)

        assert metadataUrl == 'a'
        assert namespace == 'b'
        assert resource == 'c'

    def test_mix(self):
        argv = ['--metadataUrl', 'a', '-n', 'b', '--resource', 'c']

        metadataUrl, namespace, resource = Generator.parse_args(argv, lambda: None)

        assert metadataUrl == 'a'
        assert namespace == 'b'
        assert resource == 'c'


class Test_conversions(object):

    @mark.parametrize('input,expected', [
        ('camelCase', 'camel_case'),
        ('nocamel', 'nocamel'),
        ('PascalCase','pascal_case'),
        ('kebab-case','kebab-case')
    ])
    def test_convert_camel_to_snake(self, input, expected):
        assert Generator._convert_camel_to_snake(input) == expected

    @mark.parametrize('input,expected', [
        ('noDash', 'noDash'),
        ('camel-case', 'camelCase'),
        ('Camel-Case', 'camelCase'),
        ('three-part-word', 'threePartWord'),
        ('--', '')
    ])
    def test_convert_kebab_to_camel(self, input, expected):
        assert Generator._convert_kebab_to_camel(input) == expected


class Test_build_reference_dictionary(object):
    # A simple scenario
    def test_accountCodeReference(self):
        o = Generator._build_reference_dictionary(SAMPLE_DATA, 'edFi_accountCodeReference')
        expected = {
            'accountClassificationDescriptor': "build_descriptor('AccountClassification', 'PLACEHOLDER')",
            'accountCodeNumber': "'PLACEHOLDER'",
            'educationOrganizationId': 0,
            'fiscalYear': 'current_year()'
        }
        assert o == expected

    # More complex - has a reference
    def test_accountAccountCode(self):
        o = Generator._build_reference_dictionary(SAMPLE_DATA, 'edFi_accountAccountCode')
        expected = {
            'accountCodeReference': {
                'accountClassificationDescriptor': "build_descriptor('AccountClassification', 'PLACEHOLDER')",
                'accountCodeNumber': "'PLACEHOLDER'",
                'educationOrganizationId': 0,
                'fiscalYear': 'current_year()'
            }
        }
        assert o == expected

    # Multiple references, and an array
    def test_account(self):
        o = Generator._build_reference_dictionary(SAMPLE_DATA, 'edFi_account')
        expected = {
            'accountCodes': [{
                'accountCodeReference': {
                    'accountClassificationDescriptor': "build_descriptor('AccountClassification', 'PLACEHOLDER')",
                    'accountCodeNumber': "'PLACEHOLDER'",
                    'educationOrganizationId': 0,
                    'fiscalYear': 'current_year()'
                }
            }],
            'accountIdentifier': 'UniqueIdAttribute()',
            'educationOrganizationReference': {
                'educationOrganizationId': 0
            },
            'fiscalYear': 'current_year()',
            'id': 'UniqueIdAttribute()'
        }
        assert o == expected


class Test_flatten_dictionary(object):
    def test_fully_loaded_dictionary(self):
        input = {
            'accountCodes': [{
                'accountCodeReference': {
                    'accountClassificationDescriptor': "build_descriptor('AccountClassification', 'PLACEHOLDER')",
                    'accountCodeNumber': "'PLACEHOLDER'",
                    'educationOrganizationId': 0,
                    'fiscalYear': 'current_year()'
                }
            }],
            'accountIdentifier': 'UniqueIdAttribute()',
            'educationOrganizationReference': {
                'educationOrganizationId': 0
            },
            'fiscalYear': 'current_year()',
            'id': 'UniqueIdAttribute()'
        }
        expected = """    id = UniqueIdAttribute()
    accountCodes = [{\'accountCodeReference\': {\'accountCodeNumber\': \'PLACEHOLDER\', \'educationOrganizationId\': 0, \'accountClassificationDescriptor\': build_descriptor(\'AccountClassification\', \'PLACEHOLDER\'), \'fiscalYear\': current_year()}}]
    educationOrganizationReference = {\'educationOrganizationId\': 0}
    accountIdentifier = UniqueIdAttribute()
    fiscalYear = current_year()
"""

        actual = Generator._flatten_dictionary(input)

        assert actual == expected


SAMPLE_DATA = {
    "swagger": "2.0",
    "basePath": "/data/v3",
    "consumes": [
        "application/json"
    ],
    "definitions": {
        "edFi_account": {
            "properties": {
                "id": {
                    "description": "",
                    "type": "string"
                },
                "accountCodes": {
                    "description": "An unordered collection of accountAccountCodes. The set of account codes defined for the education accounting system organized by account code type (e.g., fund, function, object) that map to the account.",
                    "items": {
                        "$ref": "#/definitions/edFi_accountAccountCode"
                    },
                    "type": "array"
                },
                "accountIdentifier": {
                    "description": "The alphanumeric string that identifies the account.",
                    "x-Ed-Fi-isIdentity": True,
                    "maxLength": 50,
                    "type": "string"
                },
                "fiscalYear": {
                    "description": "The financial accounting year.",
                    "format": "int32",
                    "x-Ed-Fi-isIdentity": True,
                    "type": "integer"
                },
                "educationOrganizationReference": {
                    "$ref": "#/definitions/edFi_educationOrganizationReference"
                },
                "accountName": {
                    "description": "A descriptive name for the account.",
                    "maxLength": 100,
                    "type": "string"
                },
                "aggregateHashValue": {
                    "description": "",
                    "format": "int64",
                    "type": "integer"
                },
                "_etag": {
                    "description": "A unique system-generated value that identifies the version of the resource.",
                    "type": "string"
                }
            },
            "required": [
                "accountIdentifier",
                "fiscalYear",
                "id",
                "accountCodes",
                "educationOrganizationReference"
            ],
            "type": "object"
        },
        "edFi_accountAccountCode": {
            "properties": {
                "accountCodeReference": {
                    "$ref": "#/definitions/edFi_accountCodeReference"
                }
            },
            "required": [
                "accountCodeReference"
            ],
            "type": "object"
        },
        "edFi_accountCodeReference": {
            "properties": {
                "accountClassificationDescriptor": {
                    "description": "The type of account code associated with the account.",
                    "maxLength": 306,
                    "type": "string"
                },
                "accountCodeNumber": {
                    "description": "An account code defined for the education accounting system by the education organization.",
                    "maxLength": 50,
                    "type": "string"
                },
                "educationOrganizationId": {
                    "description": "The identifier assigned to an education organization.",
                    "format": "int32",
                    "type": "integer"
                },
                "fiscalYear": {
                    "description": "The financial accounting year.",
                    "format": "int32",
                    "type": "integer"
                },
                "link": {
                    "$ref": "#/definitions/link"
                }
            },
            "required": [
                "accountClassificationDescriptor",
                "accountCodeNumber",
                "educationOrganizationId",
                "fiscalYear"
            ],
            "type": "object"
        },
        "edFi_educationOrganizationReference": {
            "properties": {
                "educationOrganizationId": {
                    "description": "The identifier assigned to an education organization.",
                    "format": "int32",
                    "type": "integer"
                },
                "link": {
                    "$ref": "#/definitions/link"
                }
            },
            "required": [
                "educationOrganizationId"
            ],
            "type": "object"
        },
        "grandBend_applicant": {
            "properties": {
                "id": {
                    "description": "",
                    "type": "string"
                },
                "applicantIdentifier": {
                    "description": "A unique alphanumeric code assigned to an applicant.",
                    "x-Ed-Fi-isIdentity": True,
                    "maxLength": 32,
                    "type": "string"
                },
                "educationOrganizationReference": {
                    "$ref": "#/definitions/edFi_educationOrganizationReference"
                },
                "addresses": {
                    "description": "An unordered collection of applicantAddresses. The set of elements that describes an address, including the street address, city, state, and ZIP code.",
                    "items": {
                        "$ref": "#/definitions/grandBend_applicantAddress"
                    },
                    "type": "array"
                },
                "birthDate": {
                    "description": "The month, day, and year on which an individual was born.",
                    "format": "date-time",
                    "type": "string"
                },
                "citizenshipStatusDescriptor": {
                    "description": "An indicator of whether or not the person is a U.S. citizen.",
                    "maxLength": 306,
                    "type": "string"
                },
                "firstName": {
                    "description": "A name given to an individual at birth, baptism, or during another naming ceremony, or through legal change.",
                    "maxLength": 75,
                    "type": "string"
                },
                "generationCodeSuffix": {
                    "description": "An appendage, if any, used to denote an individual's generation in his family (e.g., Jr., Sr., III).",
                    "maxLength": 10,
                    "type": "string"
                },
                "highestCompletedLevelOfEducationDescriptor": {
                    "description": "The extent of formal instruction an individual has received (e.g., the highest grade in school completed or its equivalent or the highest degree received).",
                    "maxLength": 306,
                    "type": "string"
                },
                "highlyQualifiedAcademicSubjectDescriptor": {
                    "description": "An applicant subject in which a teacher applicant is classified as highly qualified.",
                    "maxLength": 306,
                    "type": "string"
                },
                "highlyQualifiedTeacher": {
                    "description": "An indication of whether a teacher applicant is classified as highly qualified for his/her prospective assignment according to state definition. This attribute indicates the teacher is highly qualified for ALL Sections to be taught.",
                    "type": "boolean"
                },
                "hispanicLatinoEthnicity": {
                    "description": "An indication that the individual traces his or her origin or descent to Mexico, Puerto Rico, Cuba, Central, and South America, and other Spanish cultures, regardless of race. The term, \"Spanish origin,\" can be used in addition to \"Hispanic or Latino.\"",
                    "type": "boolean"
                },
                "lastSurname": {
                    "description": "The name borne in common by members of a family.",
                    "maxLength": 75,
                    "type": "string"
                },
                "loginId": {
                    "description": "The login ID for the user; used for security access control interface.",
                    "maxLength": 60,
                    "type": "string"
                },
                "maidenName": {
                    "description": "The person's maiden name.",
                    "maxLength": 75,
                    "type": "string"
                },
                "middleName": {
                    "description": "A secondary name given to an individual at birth, baptism, or during another naming ceremony.",
                    "maxLength": 75,
                    "type": "string"
                },
                "personalTitlePrefix": {
                    "description": "A prefix used to denote the title, degree, position, or seniority of the person.",
                    "maxLength": 30,
                    "type": "string"
                },
                "sexDescriptor": {
                    "description": "A person's gender.",
                    "maxLength": 306,
                    "type": "string"
                },
                "yearsOfPriorProfessionalExperience": {
                    "description": "The total number of years that an individual has previously held a similar professional position in one or more education institutions.",
                    "format": "double",
                    "type": "number"
                },
                "yearsOfPriorTeachingExperience": {
                    "description": "The total number of years that an individual has previously held a teaching position in one or more education institutions.",
                    "format": "double",
                    "type": "number"
                },
                "_etag": {
                    "description": "A unique system-generated value that identifies the version of the resource.",
                    "type": "string"
                }
            },
            "required": [
                "applicantIdentifier",
                "firstName",
                "id",
                "lastSurname",
                "educationOrganizationReference"
            ],
            "type": "object"
        }
    }
}