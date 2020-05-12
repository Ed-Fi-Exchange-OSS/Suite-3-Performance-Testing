import traceback
from greenlet import GreenletExit

from locust import task, TaskSequence, TaskSet, runners
from locust.exception import StopLocust, InterruptTaskSet

from edfi_performance.api.client import EdFiAPIClient
from edfi_performance.tasks import EdFiTaskSet


class EdFiPipecleanTestBase(EdFiTaskSet):
    """
    Base class for all "pipeclean" tests for the Ed-Fi ODS API.  Pipeclean
    tests methodically exercise all five endpoints for a given resource:
    - GET list:     GET /resources
    - POST list:    POST /resources
    - GET detail:   GET /resources/{id}
    - PUT:          PUT /resources/{id}
    - DELETE:       DELETE /resources/{id}

    Required attributes on this class:
    - `client_class`: See documentation for parent class `EdFiTaskSet`.
    - `update_attribute_name`: For the PUT scenario, the name of the attribute
        to be updated on the resource instance, e.g. `firstName` or `endDate`.
    - `update_attribute_value`: The new value for the update, e.g. `"Linda"` or
        `"2018-05-01"`.

    Optional methods:
    - `get_create_with_dependencies_kwargs`: If this test's `client_class`
        requires parameters for `create_with_dependencies`, override this function to
        return those as a dict.  `self.create_with_dependencies` will pass them
        through to the client.

    Usage:
    ```
    class ExamplePipecleanTest(EdFiPipecleanTestBase):
        client_class = ExampleClient

        update_attribute_name = 'firstName'
        update_attribute_value = "Woodrow"

        def get_create_with_dependencies_kwargs(self):
            return {'schoolId': 255901107}
    ```
    """
    _resource_reference = None
    _resource_id = None

    update_attribute_name = None
    update_attribute_value = None

    @task
    def run_pipeclean_scenario(self):
        self._run_pipeclean_scenario()

    def _run_pipeclean_scenario(self):
        try:
            self._touch_get_list_endpoint()
            self._touch_post_endpoint()
            if self.is_invalid_response(self._resource_id):
                self._proceed_to_next_pipeclean_test()
            self._touch_get_detail_endpoint(self._resource_id)
            self._touch_put_endpoint(self._resource_id, self._resource_reference['attributes'])
            self._touch_delete_endpoint(self._resource_reference)
            self._proceed_to_next_pipeclean_test()  # Pass on to the next pipeclean test
        except (StopLocust, GreenletExit, InterruptTaskSet, KeyboardInterrupt):
            raise
        except Exception:
            traceback.print_exc()
            self._proceed_to_next_pipeclean_test()

    def run_get_only_pipeclean_scenario(self):
        try:
            response = self._touch_get_list_endpoint()
            if self.is_invalid_response(response):
                self._proceed_to_next_pipeclean_test()
            first_resource = response[0]
            resource_id = first_resource['id']
            self._touch_get_detail_endpoint(resource_id)
            self._proceed_to_next_pipeclean_test()
        except (StopLocust, GreenletExit, InterruptTaskSet, KeyboardInterrupt):
            raise
        except Exception:
            traceback.print_exc()
            self._proceed_to_next_pipeclean_test()

    def get_create_with_dependencies_kwargs(self):
        return {}

    def _touch_get_list_endpoint(self):
        return self.get_list()

    def _touch_post_endpoint(self):
        # Note that this may POST to other endpoints to create dependencies
        self._resource_reference = self.create_with_dependencies(**self.get_create_with_dependencies_kwargs())
        self._resource_id = self._resource_reference['resource_id']

    def _touch_get_detail_endpoint(self, resource_id):
        self.get_item(resource_id)

    def _touch_put_endpoint(self, resource_id, default_attributes):
        if self.update_attribute_name is None or self.update_attribute_value is None:
            raise ValueError(
                "Subclasses of {} must define update_attribute_name and"
                " update_attribute_value".format('EdFiPipecleanTestBase'))
        attrs = default_attributes
        attrs[self.update_attribute_name] = self.update_attribute_value
        self.update(resource_id, **attrs)

    def _touch_delete_endpoint(self, reference):
        self.delete_from_reference(reference)

    def _proceed_to_next_pipeclean_test(self):
        self.interrupt()


class EdFiPipecleanTaskSequence(TaskSequence):
    """
    Base class for the sequence of tasks involved in a pipeclean test.  Logs in
    to get a token to be shared among all child task sets.

    The pipeclean_tests.py locustfile will automatically detect and append each
    child task set to be run to the `tasks` attribute.
    """
    tasks = []

    shared_token = None

    def __init__(self, *args, **kwargs):
        super(EdFiPipecleanTaskSequence, self).__init__(*args, **kwargs)
        client = EdFiAPIClient(self.locust.host)
        self.shared_token = client.token


class EdFiPipecleanTestTerminator(TaskSet):
    """
    Append this to the end of a sequence of tasks to terminate the test run
    after all other tasks finish.

    This is useful for pipeclean tests since they want to hit each endpoint
    once and then exit.

    Using this terminator with more than one Locust client will have
    unpredictable behavior: the first client to hit this task will cause
    the entire Locust run to quit.
    """
    @task
    def finish_pipeclean_test_run(self):
        runners.locust_runner.quit()
