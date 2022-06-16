# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.


import os
from edfi_performance_test.helpers.main_arguments import MainArguments

def get_config_value(key):
   return os.environ.get(key)

def set_config_values(args: MainArguments):
   os.environ["key"] = args.key
   os.environ["baseUrl"] = args.baseUrl
   os.environ["deleteResources"] = str(args.deleteResources)
   os.environ["failDeliberately"] = str(args.failDeliberately)
   os.environ["ignoreCertificateErrors"] = str(args.ignoreCertificateErrors)
   os.environ["secret"] = args.secret
