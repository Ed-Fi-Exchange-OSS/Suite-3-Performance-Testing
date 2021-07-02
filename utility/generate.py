# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import sys

import generate_lib as Generator


VERSION = '1.0.0'

def main(argv):

    config = Generator.parse_args(argv, _display_help)
    if not config or not config[0]:
        # Assume the library already generated a helpful message on screen
        sys.exit(2)

    metadataUrl, namespace, resource = config

    metadata = Generator.retrieve_metadata(metadataUrl)

    factory = Generator.create_factory(metadata, namespace, resource)
    fileName = Generator.build_file_name(['factories', 'resources'], resource)
    Generator.write_file(factory, fileName)

    client = Generator.create_client(namespace, resource)
    fileName = Generator.build_file_name(['api', 'client'], resource)
    Generator.write_file(client, fileName)

    pipeclean = Generator.create_pipeclean_test(resource)
    fileName = Generator.build_file_name(['tasks', 'pipeclean'], resource)
    Generator.write_file(pipeclean, fileName)

    volume = Generator.create_volume_test(resource)
    fileName = Generator.build_file_name(['tasks', 'volume'], resource)
    Generator.write_file(volume, fileName)

    print ('Boilerplate files have been written. Don\'t forget to review them carefully:')
    print (Generator.files_created(resource))


def _display_help():
    """
Code generator for creating boilerplate files to execute performance tests on a
new resource - including extensions. Version {version}.

In the following examples, if you break the command across multiple lines as
shown, then you'll need to use the proper line continuation character for your
environment: \\ when using Bash, ^ in Windows cmd.exe, and ` in PowerShell.
PowerShell version is shown. Please note that the resource name is generally
singular, not plural.

> python generate.py `
    -m <metadataUrl> `
    -n <namespace> `
    -r <resource>

or use the long form:

> python generate.py `
    --metadataUrl <metadataUrl> `
    --namespace <namespace> `
    --resource <resource>

example for the Grand Bend "Applicants" resource using the default metadata
endpoint for ODS version 3:

> python generate.py `
    -m http://localhost:54746/metadata/data/v3/resources/swagger.json `
    -n grand-bend `
    -r applicant

This command will create the following new files under the `edfi_performance`
directory:
{filesCreated}

Please review these files carefully, especially the factory file. When
generating for new core resources, simply use "ed-fi" as the namespace.
""".format(
        version = VERSION,
        filesCreated = Generator.files_created('applicant')
    )


if __name__ == "__main__":
   main(sys.argv[1:])
