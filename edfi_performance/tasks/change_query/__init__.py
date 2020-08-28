# SPDX-License-Identifier: Apache-2.0
# Licensed to the Ed-Fi Alliance under one or more agreements.
# The Ed-Fi Alliance licenses this file to you under the Apache License, Version 2.0.
# See the LICENSE and NOTICES files in the project root for more information.

import timeit
import traceback

from greenlet import GreenletExit
from locust import task, TaskSequence, TaskSet, runners
from locust.exception import StopLocust, InterruptTaskSet
from edfi_performance.api.basic_client import EdFiBasicAPIClient
from edfi_performance.config import get_config_value, set_change_version_value


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
    _client = None

    def __init__(self, parent, *args, **kwargs):
        super(EdFiChangeQueryTestBase, self).__init__(parent, *args, **kwargs)
        self._client = EdFiBasicAPIClient()

    @task
    def run_change_query_scenario(self):
        try:
            self._iterate_through_resource_table()
            self._proceed_to_next_change_query_test()
        except (StopLocust, GreenletExit, InterruptTaskSet, KeyboardInterrupt):
            raise
        except Exception:
            traceback.print_exc()
            self._proceed_to_next_change_query_test()

    def _iterate_through_resource_table(self):
        num_of_results = 0
        offset = 0
        limit = 100
        time = 0
        min_change_version = get_config_value('newest_change_version')
        if min_change_version != 0:
            min_change_version += 1

        while True:
            if offset > 0 and offset % 10000 == 0:
                print 'Offset has reached: {}'.format(offset)
            query = "?offset={}&limit={}&minChangeVersion={}".format(offset, limit, min_change_version)
            start = timeit.default_timer()
            endpoint = self.endpoint
            results = self._touch_get_list_endpoint(endpoint, query)
            stop = timeit.default_timer()
            time += (stop - start)
            if results is None:
                break
            num_of_results += len(results)
            if len(results) < limit:
                break
            offset += limit

        print '{} Sync: {} seconds'.format(endpoint, time)
        print '{} results returned for {}'.format(num_of_results, endpoint)

    def _touch_get_list_endpoint(self, endpoint, query):
        return self._client.get_list(endpoint, query)

    def _proceed_to_next_change_query_test(self):
        self.interrupt()


class EdFiChangeQueryTaskSequence(TaskSequence):
    """
    Base class for the sequence of tasks involved in a Change Query test.  Logs in
    to get a token to be shared among all child task sets.

    The change_query_tests.py locustfile will automatically detect and append each
    child task set to be run to the `tasks` attribute.
    """
    tasks = []

    def __init__(self, *args, **kwargs):
        super(EdFiChangeQueryTaskSequence, self).__init__(*args, **kwargs)


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

    _client = None

    def __init__(self, *args, **kwargs):
        super(EdFiChangeQueryTestTerminator, self).__init__(*args, **kwargs)
        self._client = EdFiBasicAPIClient('/data/v3')

    def _update_newest_change_version(self):
        available_change_versions = self._client.get_list('availableChangeVersions')
        if available_change_versions is not None:
            newest_change_version = available_change_versions['NewestChangeVersion']
            set_change_version_value(newest_change_version)
            print 'Current value of NewestChangeVersion: {}'.format(newest_change_version)

    @task
    def finish_change_query_test_run(self):
        self._update_newest_change_version()
        runners.locust_runner.quit()
