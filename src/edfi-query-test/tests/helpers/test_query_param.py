# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import pytest

from edfi_query_test.helpers.query_param import QueryParam


def describe_QueryParam_class():
    def describe_when_constructing():
        def it_sets_name_property():
            # Arrange & Act
            param = QueryParam(name="studentUniqueId")
            
            # Assert
            assert param.name == "studentUniqueId"

        def it_supports_descriptor_names():
            # Arrange & Act  
            param = QueryParam(name="gradingPeriodDescriptor")
            
            # Assert
            assert param.name == "gradingPeriodDescriptor"

        def it_supports_reference_names():
            # Arrange & Act
            param = QueryParam(name="schoolReference")
            
            # Assert
            assert param.name == "schoolReference"

    def describe_when_using_dataclass_features():
        def it_supports_equality_comparison():
            # Arrange
            param1 = QueryParam(name="studentUniqueId")
            param2 = QueryParam(name="studentUniqueId") 
            param3 = QueryParam(name="schoolId")
            
            # Act & Assert
            assert param1 == param2
            assert param1 != param3

        def it_supports_string_representation():
            # Arrange
            param = QueryParam(name="studentUniqueId")
            
            # Act
            result = str(param)
            
            # Assert
            assert "QueryParam" in result
            assert "studentUniqueId" in result

        def it_supports_hashing():
            # Arrange
            param1 = QueryParam(name="studentUniqueId")
            param2 = QueryParam(name="schoolId")
            
            # Act - should not raise exception
            param_set = {param1, param2}
            
            # Assert
            assert len(param_set) == 2