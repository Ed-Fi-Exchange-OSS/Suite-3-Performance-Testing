# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

from typing import List


import pytest


from edfi_paging_test.helpers.argparser import parse_main_arguments


BASEURL = "http://localhost:54746"
KEY = "empty"
SECRET = "emptySecret"


def _baseUrl_args() -> List[str]:
    return ["--baseUrl", BASEURL]


def _key_args() -> List[str]:
    return ["--key", KEY]


def _secret_args() -> List[str]:
    return ["--secret", SECRET]


def _assert_no_messages(capsys) -> None:
    out, err = capsys.readouterr()

    assert err == "", "There should be an error message"
    assert out == "", "There should not be an output message"


def _assert_error_message(capsys) -> None:
    out, err = capsys.readouterr()

    assert err != "", "There should be an error message"
    assert out == "", "There should not be an output message"


def describe_given_arguments_do_not_include_baseUrl() -> None:
    def it_should_show_help(capsys) -> None:
        with pytest.raises(SystemExit):
            args = [
                *_key_args(),
                *_secret_args(),
                ]

            parse_main_arguments(args)
            _assert_error_message(capsys)


def describe_given_arguments_do_not_include_key() -> None:
    def it_should_show_help(capsys) -> None:
        with pytest.raises(SystemExit):
            args = [
                *_baseUrl_args(),
                *_secret_args(),
                ]

            parse_main_arguments(args)
            _assert_error_message(capsys)


def describe_given_arguments_do_not_include_secret() -> None:
    def it_should_show_help(capsys) -> None:
        with pytest.raises(SystemExit):
            args = [
                *_baseUrl_args(),
                *_key_args(),
                ]

            parse_main_arguments(args)
            _assert_error_message(capsys)
