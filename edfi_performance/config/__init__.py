# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import json
import os
_config = None


def _get_config_file_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.join(current_dir, '..')
    current_dir = os.path.join(current_dir, '..')
    return os.path.join(current_dir, 'locust-config.json')


def _load_config():
    required_keys = ['host', 'client_id', 'client_secret', 'delete_resources', 'fail_deliberately']
    global _config

    config_file = _get_config_file_path()
    with open(config_file, 'r') as infile:
        _config = json.loads(infile.read())
    for key in required_keys:
        if key not in _config:
            raise ValueError("'{}' is a required key in {}".format(key, config_file))


def get_config_value(key):
    if _config is None:
        _load_config()
    return _config[key]
