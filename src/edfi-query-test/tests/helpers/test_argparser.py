# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import os
from typing import List
import sys

import pytest

from edfi_query_test.helpers.argparser import parse_main_arguments
from edfi_query_test.helpers.main_arguments import MainArguments
from edfi_query_test.helpers.output_format import OutputFormat
from edfi_query_test.helpers.log_level import LogLevel


BASEURL = "http://localhost:54746"
KEY = "testkey"
SECRET = "testsecret"


def _baseUrl_args() -> List[str]:
    return ["--baseUrl", BASEURL]


def _key_args() -> List[str]:
    return ["--key", KEY]


def _secret_args() -> List[str]:
    return ["--secret", SECRET]


def _required_args() -> List[str]:
    return _baseUrl_args() + _key_args() + _secret_args()


def describe_parse_main_arguments():
    def describe_given_required_arguments():
        def it_sets_required_properties():
            # Arrange
            sys.argv = ["query_test"] + _required_args()
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.baseUrl == BASEURL
            assert result.key == KEY
            assert result.secret == SECRET

        def it_sets_default_values():
            # Arrange  
            sys.argv = ["query_test"] + _required_args()
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.pageSize == 100
            assert result.connectionLimit == 5
            assert result.ignoreCertificateErrors is False
            assert result.contentType == OutputFormat.CSV
            assert result.log_level == LogLevel.INFO

    def describe_given_optional_arguments():
        def it_overrides_page_size():
            # Arrange
            sys.argv = ["query_test"] + _required_args() + ["--pageSize", "50"]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.pageSize == 50

        def it_sets_ignore_certificate_errors():
            # Arrange
            sys.argv = ["query_test"] + _required_args() + ["--ignoreCertificateErrors"]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.ignoreCertificateErrors is True

        def it_sets_connection_limit():
            # Arrange
            sys.argv = ["query_test"] + _required_args() + ["--connectionLimit", "10"]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.connectionLimit == 10

        def it_sets_output_directory():
            # Arrange
            output_dir = "./test_output"
            sys.argv = ["query_test"] + _required_args() + ["--output", output_dir]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.output == output_dir

        def it_sets_content_type_json():
            # Arrange
            sys.argv = ["query_test"] + _required_args() + ["--contentType", "JSON"]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.contentType == OutputFormat.JSON

        def it_sets_resource_list():
            # Arrange
            sys.argv = ["query_test"] + _required_args() + ["--resourceList", "Students", "Schools"]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.resourceList == ["Students", "Schools"]

        def it_sets_log_level():
            # Arrange
            sys.argv = ["query_test"] + _required_args() + ["--logLevel", "DEBUG"]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.log_level == LogLevel.DEBUG

        def it_sets_description():
            # Arrange
            description = "Custom test run"
            sys.argv = ["query_test"] + _required_args() + ["--description", description]
            
            # Act
            result = parse_main_arguments()
            
            # Assert
            assert result.description == description