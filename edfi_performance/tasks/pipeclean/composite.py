import traceback
from greenlet import GreenletExit

from locust import task
from locust.exception import StopLocust, InterruptTaskSet

from edfi_performance.api.client import _import_from_dotted_path
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class EdFiCompositePipecleanTestBase(EdFiPipecleanTestBase):
    composite_resources = None

    @task
    def run_pipeclean_scenario(self):
        self._run_pipeclean_scenario()

    def _run_pipeclean_scenario(self):
        try:
            response = self._touch_get_list_endpoint()
            if self.is_invalid_response(response):
                self._proceed_to_next_pipeclean_test()
            first_resource = response[0]
            resource_id = first_resource['id']
            self._touch_get_detail_endpoint(resource_id)
            for resource in self.composite_resources:
                if self._api_client.endpoint != resource:
                    self._touch_get_composite_list_endpoint(resource, self._get_composite_client().shared_id(resource))
            self._proceed_to_next_pipeclean_test()
        except (StopLocust, GreenletExit, InterruptTaskSet, KeyboardInterrupt):
            raise
        except Exception:
            traceback.print_exc()
            self._proceed_to_next_pipeclean_test()

    def _touch_get_composite_list_endpoint(self, resource, resource_id):
        return self.get_composite_list(resource, resource_id)

    def _get_composite_client(self):
        class_name = self.__class__.__name__.replace('PipecleanTest', 'Client')
        class_path = self.__class__.__module__.replace('tasks.pipeclean', 'api.client') + '.' + class_name
        self.client_class = _import_from_dotted_path(class_path)
        return self.client_class.__bases__[0]
