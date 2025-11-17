# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# See the LICENSE and NOTICES files in the project root for more information.

import threading
from typing import Any, Dict

from edfi_performance_test.api.client.school import SchoolClient
from edfi_performance_test.api.client.course_offering import CourseOfferingClient
from edfi_performance_test.api.client.class_period import ClassPeriodClient
from edfi_performance_test.api.client.location import LocationClient


_fixtures_lock = threading.Lock()
_shared_school_natural_key: Dict[str, Any] | None = None
_shared_course_offering_natural_key: Dict[str, Any] | None = None
_shared_class_period_natural_key: Dict[str, Any] | None = None
_shared_location_natural_key: Dict[str, Any] | None = None


def _ensure_edfi_client_initialized() -> None:
    """
    Ensure that EdFiAPIClient has a client and token set before using
    client-level helpers like `create_shared_resource`.

    This function assumes that BatchVolumeTestUser has already associated
    `EdFiAPIClient.client` and `EdFiAPIClient.token` via its login flow.
    """
    # SchoolClient and CourseOfferingClient rely on EdFiAPIClient.client and token
    # being configured; no additional work is needed here beyond importing them.
    # The imports at module scope ensure the classes are loaded.
    return


def get_or_create_shared_school() -> Dict[str, Any]:
    """
    Create (once) and return the natural key for a shared School fixture.

    This uses the existing SchoolClient.shared_elementary_school_id helper,
    which ultimately calls EdFiAPIClient.create_shared_resource and the
    SchoolFactory to create a School and related resources. For batch tests,
    we only need the natural key: schoolId.
    """
    global _shared_school_natural_key

    if _shared_school_natural_key is not None:
        return _shared_school_natural_key

    with _fixtures_lock:
        if _shared_school_natural_key is not None:
            return _shared_school_natural_key

        _ensure_edfi_client_initialized()
        school_id = SchoolClient.shared_elementary_school_id()
        _shared_school_natural_key = {"schoolId": school_id}
        return _shared_school_natural_key


def get_or_create_shared_course_offering() -> Dict[str, Any]:
    """
    Create (once) and return the natural key for a shared CourseOffering
    fixture.

    For the DMS batch API, the natural key for courseOfferings includes:
    - courseOfferingReference__localCourseCode
    - courseOfferingReference__schoolId
    - courseOfferingReference__schoolYear
    - courseOfferingReference__sessionName

    We reuse the existing CourseOfferingClient.create_with_dependencies to
    create a valid offering and then capture the attributes necessary to
    reference it.
    """
    global _shared_course_offering_natural_key

    if _shared_course_offering_natural_key is not None:
        return _shared_course_offering_natural_key

    with _fixtures_lock:
        if _shared_course_offering_natural_key is not None:
            return _shared_course_offering_natural_key

        _ensure_edfi_client_initialized()

        # Create a course offering and its dependencies using the existing
        # client behavior, then extract its natural key attributes.
        client = CourseOfferingClient(
            CourseOfferingClient.client, token=CourseOfferingClient.token
        )
        reference = client.create_with_dependencies()
        attrs = reference["attributes"]

        _shared_course_offering_natural_key = {
            "localCourseCode": attrs["localCourseCode"],
            "schoolId": attrs["schoolId"],
            "schoolYear": attrs["schoolYear"],
            "sessionName": attrs["sessionReference"]["sessionName"],
        }

        return _shared_course_offering_natural_key


def get_or_create_shared_class_period() -> Dict[str, Any]:
    """
    Create (once) and return the natural key for a shared ClassPeriod fixture.

    The Section resource references classPeriods via:
    - classPeriodReference__classPeriodName
    - classPeriodReference__schoolId
    """
    global _shared_class_period_natural_key

    if _shared_class_period_natural_key is not None:
        return _shared_class_period_natural_key

    with _fixtures_lock:
        if _shared_class_period_natural_key is not None:
            return _shared_class_period_natural_key

        _ensure_edfi_client_initialized()

        client = ClassPeriodClient(ClassPeriodClient.client, token=ClassPeriodClient.token)
        reference = client.create_with_dependencies()
        attrs = reference["attributes"]

        _shared_class_period_natural_key = {
            "classPeriodName": attrs["classPeriodName"],
            "schoolId": attrs["schoolReference"]["schoolId"],
        }

        return _shared_class_period_natural_key


def get_or_create_shared_location() -> Dict[str, Any]:
    """
    Create (once) and return the natural key for a shared Location fixture.

    The Section resource references location via:
    - classroomIdentificationCode
    - schoolId
    """
    global _shared_location_natural_key

    if _shared_location_natural_key is not None:
        return _shared_location_natural_key

    with _fixtures_lock:
        if _shared_location_natural_key is not None:
            return _shared_location_natural_key

        _ensure_edfi_client_initialized()

        client = LocationClient(LocationClient.client, token=LocationClient.token)
        reference = client.create_with_dependencies()
        attrs = reference["attributes"]

        _shared_location_natural_key = {
            "classroomIdentificationCode": attrs["classroomIdentificationCode"],
            "schoolId": attrs["schoolReference"]["schoolId"],
        }

        return _shared_location_natural_key
