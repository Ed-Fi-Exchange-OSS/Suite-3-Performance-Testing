import sys
import getopt
import urllib2
import json
import os


def parse_args(argv, display_help):
    metadataUrl = ''
    namespace = ''
    resource = ''

    try:
        opts, _ = getopt.getopt(
            argv,
            "hm:n:r:",
            ["metadataUrl=","namespace=","resource=","help"]
        )
    except getopt.GetoptError:
        display_help()
        return ((),(),())

    for opt, arg in opts:
        if opt in ('-h','--help'):
            # _display_help()
            raise Exception("displaying help")
        elif opt in ("-m", "--metadataUrl"):
            metadataUrl = arg
        elif opt in ("-n", "--namespace"):
            namespace = arg
        elif opt in ("-r", "--resource"):
            resource = arg

    if metadataUrl == '' or namespace == '' or resource == '':
        display_help()
        return ((),(),())

    return metadataUrl, namespace, resource


def build_file_name(directories, resource):
    path = os.path.join(
        '..',
        'edfi_performance'
    )
    if isinstance(directories, list):
        for item in directories:
            path = os.path.join(
                path,
                item
            )
    else:
        path = os.path.join(
            path,
            directories
        )
    path = os.path.join(
        path,
        '{resource}.py'.format(
            resource = _convert_camel_to_snake(resource)
        )
    )
    return path


def files_created(resource):
    return """
* edfi_performance/api/client/{resource}.py
* edfi_performance/api/factories/{resource}.py
* edfi_performance/api/tasks/pipeclean/{resource}.py
* edfi_performance/api/tasks/volume/{resource}.py
""".format(resource = _convert_camel_to_snake(resource))


# Load Json into a Python object
def retrieve_metadata(metadataUrl):
    req = urllib2.Request(metadataUrl)
    opener = urllib2.build_opener()

    f = opener.open(req)
    metadata = json.loads(f.read())
    f.close()

    return metadata


def create_factory(metadata, namespace, resource):
    template = """
import factory
from edfi_performance.factories import APIFactory
from edfi_performance.factories.descriptors.utils import build_descriptor
from edfi_performance.factories.utils import UniqueIdAttribute, current_year, formatted_date, RandomSuffixAttribute, RandomDateAttribute


class {resource}Factory(APIFactory):
    # TODO: carefully review the values below, replacing "PLACEHOLDER" with
    # an appropriate value. Double-check that all foreign key references are
    # setup correctly, including choosing an appropriate descriptor value. See
    # docs/how-to-create-tests.md for instructions on adding dependencies.
""".format(resource = resource.title())

    defKey = '{namespace}_{resource}'.format(
        namespace = _convert_kebab_to_camel(namespace),
        resource = resource
    )
    resources = _build_reference_dictionary(metadata, defKey)
    template += _flatten_dictionary(resources)

    return template


def _flatten_dictionary(dict_) :
    flat = ''
    for key, value in dict_.items():
        # Map the highest-level (outermost) dictionary items into line-by-line
        # strings, so that the output file has separate lines of code rather
        # than one big dictionary.
        flat += '{indent}{key} = {value}\n'.format(
            indent='    ',
            key=key,
            value=value
        )

    # when value is itself a dictionary, formatting it into the string as done
    # above ends up wrapping extra, un-wanted quotation marks around some 
    # elements. Remove those extra quotations and extra apostrophes.
    flat = flat.replace('"', '')
    keywords = ['UniqueIdAttribute', 'current_year', 'formatted_date', 'RandomSuffixAttribute', 'RandomDateAttribute']
    for word in keywords:
        flat = flat.replace("'"+word+"()'", word+'()')

    return flat

def _build_reference_dictionary(metadata, reference):
    resources = {}

    refDefinition = None
    if '$ref' in reference:
        # extract the desired resource name from $ref item
        refItems = reference['$ref'].split('/')
        refItems.reverse()
        refDefinition = metadata['definitions'][refItems[0]]
    else:
        refDefinition = metadata['definitions'][reference]

    for item in refDefinition['required']:
        prop = refDefinition['properties'][item]
        encodedItem = item.encode('utf-8')

        type_ = prop.get('type', '')
        format_ = prop.get('format', '')

        if item.endswith('Descriptor'):
            descriptor = item.replace('Descriptor','')
            # Capitalize first letter without affecting the rest of the string
            descriptor = descriptor[0].upper() + descriptor[1:]
            resources[encodedItem] = 'build_descriptor(\'{descriptor}\', \'PLACEHOLDER\')'.format(
                descriptor=descriptor
            )
        elif 'x-Ed-Fi-isIdentity' in prop and type_ == 'string':
            resources[encodedItem] = 'UniqueIdAttribute()'
        elif item.endswith('Year') and type_ == "integer":
            resources[encodedItem] = 'current_year()'
        elif item.endswith('Date') and format_ == "date-time":
            resources[encodedItem] = 'RandomDateAttribute()'                     
        elif item == "id":
            resources[encodedItem] = 'UniqueIdAttribute()'
        elif type_:
            # Using a dictionary as replacement for switch statement, with
            # lambda used because straight-up call to value['items'] fails
            # at runtime for non arrays.
            placeHolders = {
                'boolean': (lambda arg: True),
                'integer': (lambda arg: 0),
                'number': (lambda arg: 0.0),
                'array': (
                    lambda arg: [_build_reference_dictionary(metadata, arg['items'])]
                )
            }
            value = placeHolders.get(type_, (lambda arg: '\'PLACEHOLDER\''))(prop)
            resources[encodedItem] = value
        elif '$ref' in prop:
            resources[encodedItem] = _build_reference_dictionary(metadata, prop)

    return resources


def create_client(namespace, resource):
    template = """
from edfi_performance.api.client import EdFiAPIClient


class {capitalizedResource}Client(EdFiAPIClient):
    endpoint = '{lowerResource}s'
""".format(
        capitalizedResource = resource.title(),
        lowerResource = resource.lower(),
        namespace = namespace
    )

    if namespace != 'ed-fi':
        template += """
    # Because this is in an extension, override the prefix in the base class
    API_PREFIX =  '/data/v3/{namespace}'
""".format(namespace = namespace)

    return template


def create_pipeclean_test(resource):
    template = """
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class {capitalizedResource}PipecleanTest(EdFiPipecleanTestBase):
    # TODO: choose a valid attribute to update and set a valid value
    update_attribute_name = 'PLACEHOLDER_attribute'
    update_attribute_value = 'PLACEHOLDER_value'
""".format(
        capitalizedResource = resource.title()
    )

    return template


def create_volume_test(resource):
    template = """
from locust import task

from edfi_performance.tasks.volume import EdFiVolumeTestBase


class {capitalizedResource}VolumeTest(EdFiVolumeTestBase):
    @task
    def run_scenarios(self):
        # TODO: choose a valid attribute to update and set a valid value
        self.run_scenario('PLACEHOLDER_attribute', 'PLACEHOLDER_value')
""".format(
        capitalizedResource = resource.title()
    )

    return template


def _convert_kebab_to_camel(input):
    if '-' in input:
        components = input.split('-')
        return components[0].lower() + ''.join(x.title() for x in components[1:])
    else:
        return input


def _convert_camel_to_snake(input):
    output = input[0].lower()
    for x in input[1:]:
        output += ('_'+x.lower() if x.isupper() else x)

    return output


def write_file(contents, path):
    with open(path, 'w') as f:
        f.write(contents)

