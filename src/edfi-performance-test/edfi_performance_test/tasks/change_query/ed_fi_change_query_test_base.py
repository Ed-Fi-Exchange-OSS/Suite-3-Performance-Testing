# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import timeit
import traceback
import logging

from greenlet import GreenletExit
from locust import task, SequentialTaskSet, TaskSet
from locust.exception import StopUser, InterruptTaskSet
from edfi_performance_test.api.client.ed_fi_basic_api_client import (
    EdFiBasicAPIClient,
)
from edfi_performance_test.helpers.config import (
    get_config_value,
    set_change_version_value,
)


logger = logging.getLogger(__name__)


class EdFiChangeQueryTestBase(TaskSet):
    """
    Base class for all "Change Query" tests for the Ed-Fi ODS API.  Change Query
    tests methodically page through a resource list's changes, simulating a nightly
    sync client.

    The mere presence of a `EdFiChangeQueryTestBase` subclass with an endpoint name specified
    is enough to test a resource. `ExampleChangeQueryTest` would perform a Change Query test
    against resource "examples":

    Usage:
    ```
    class ExampleChangeQueryTest(EdFiChangeQueryTestBase):
        endpoint = 'examples'

    ```
    """

    def __init__(self, parent, *args, **kwargs):
        super(EdFiChangeQueryTestBase, self).__init__(parent, *args, **kwargs)
        self.api_client = EdFiBasicAPIClient(
            EdFiBasicAPIClient.client, EdFiBasicAPIClient.token, endpoint=self.endpoint
        )

    @task
    def run_change_query_scenario(self):
        try:
            self._iterate_through_resource_table()
            self._proceed_to_next_change_query_test()
        except (StopUser, GreenletExit, InterruptTaskSet, KeyboardInterrupt):
            raise
        except Exception:
            traceback.print_exc()
            self._proceed_to_next_change_query_test()

    def _iterate_through_resource_table(self):
        num_of_results = 0
        offset = 0
        limit = 100
        time = 0
        min_change_version = int(get_config_value("newest_change_version"))
        if min_change_version != 0:
            min_change_version += 1

        while True:
            if offset > 0 and offset % 10000 == 0:
                logger.info(f"Offset has reached: {format(offset)} ")
            query = "?offset={}&limit={}&minChangeVersion={}".format(
                offset, limit, min_change_version
            )
            start = timeit.default_timer()
            results = self._touch_get_list_endpoint(query)
            stop = timeit.default_timer()
            time += stop - start
            if results is None:
                break
            num_of_results += len(results)
            if len(results) < limit:
                break
            offset += limit

        logger.info(f"{format(self.endpoint)} Sync: {format(time)} secconds")

        logger.info(f"{format(num_of_results)} results returned for: {format(self.endpoint)} ")

    def _touch_get_list_endpoint(self, query):
        return self.api_client.get_list(query)

    def _proceed_to_next_change_query_test(self):
        self.interrupt()


class EdFiChangeQueryTaskSequence(SequentialTaskSet):
    """
    Base class for the sequence of tasks involved in a Change Query test.  Logs in
    to get a token to be shared among all child task sets.

    The change_query_tests.py locustfile will automatically detect and append each
    child task set to be run to the `tasks` attribute.
    """

    def __init__(self, *args, **kwargs):
        super(EdFiChangeQueryTaskSequence, self).__init__(*args, **kwargs)
        EdFiBasicAPIClient.client = self.client
        EdFiBasicAPIClient.token = None


class EdFiChangeQueryTestTerminator(TaskSet):
    """
    Append this to the end of a sequence of tasks to terminate the test run
    after all other tasks finish.

    This is useful for Change Query tests since they want to hit each changed
    resource once and then exit.

    Using this terminator with more than one Locust client will have
    unpredictable behavior: the first client to hit this task will cause
    the entire Locust run to quit.
    """

    def __init__(self, parent, *args, **kwargs):
        super(EdFiChangeQueryTestTerminator, self).__init__(parent, *args, **kwargs)
        self.api_client = EdFiBasicAPIClient(
            EdFiBasicAPIClient.client, EdFiBasicAPIClient.token, "/ChangeQueries/v1"
        )

    def _update_newest_change_version(self):
        available_change_versions = self.api_client.get_list("availableChangeVersions")
        if available_change_versions is not None:
            newest_change_version = available_change_versions["newestChangeVersion"]
            set_change_version_value(newest_change_version)

            logger.info(f"Current value of NewestChangeVersion: {format(newest_change_version)} ")

    @task
    def finish_change_query_test_run(self):
        self._update_newest_change_version()
        self.interrupt()
