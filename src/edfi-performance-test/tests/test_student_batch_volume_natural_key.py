# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

from edfi_performance_test.tasks.batch_volume.student_batch_volume import (
    StudentBatchVolumeTest,
)


def test_student_batch_volume_get_natural_key_uses_student_unique_id() -> None:
    """
    Basic unit test to ensure the StudentBatchVolumeTest constructs the
    natural key correctly from a factory-generated document.
    """
    document = {"studentUniqueId": "123456"}

    # Call get_natural_key as an instance method using the class itself as
    # the bound object, to avoid instantiating a full Locust TaskSet.
    natural_key = StudentBatchVolumeTest.get_natural_key(  # type: ignore[arg-type]
        StudentBatchVolumeTest, document
    )

    assert natural_key["studentUniqueId"] == "123456"
