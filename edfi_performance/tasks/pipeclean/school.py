from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase


class SchoolPipecleanTest(EdFiPipecleanTestBase):
    def _touch_put_endpoint(self, resource_id, attrs):
        attrs['addresses'][0]['streetNumberName'] = "456 Cedar Street"
        self.update(resource_id, **attrs)


class SchoolYearTypePipecleanTest(EdFiPipecleanTestBase):
    def _run_pipeclean_scenario(self):
        # Don't use POST, PUT, or DELETE endpoints as this resource can't be
        # created, modified, or deleted because it is a core enumeration defined by the API implementer
        self.run_get_only_pipeclean_scenario()
