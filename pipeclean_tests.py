"""
This module dynamically imports pipeclean-testing locusts for all scenarios
registered in the `tasks.pipeclean` package and combines them into a single
locust which runs each scenario in order.

In order to restrict which scenarios are run, you can name *PipecleanTest
classes on the command line in the locust invocation, and only those classes
will be added to the run.

E.g.

`locust -f pipeclean_tests.py -c 1 --no-web SchoolPipecleanTest StudentPipecleanTest`
"""
import importlib
import os
import pkgutil
import sys
from types import ModuleType

from locust import HttpLocust, TaskSet
from locust.main import parse_options

from edfi_performance.config import get_config_value
from edfi_performance.tasks.pipeclean import EdFiPipecleanTestBase, EdFiPipecleanTaskSequence, \
    EdFiPipecleanTestTerminator

# Import modules under tasks.pipeclean package so *PipecleanTest classes are registered
from edfi_performance.tasks.pipeclean.composite import EdFiCompositePipecleanTestBase
from edfi_performance.tasks.pipeclean.descriptors import AllDescriptorsPipecleanTest

tasks_submodules = [
    name for _, name, _ in pkgutil.iter_modules(
        [os.path.join('edfi_performance', 'tasks', 'pipeclean')],
        prefix='edfi_performance.tasks.pipeclean.')
]
for mod_name in tasks_submodules:
    importlib.import_module(mod_name)


# Collect *PipecleanTest classes and append them to
# EdFiPipecleanTaskSequence.tasks
_, opts, args = parse_options()
subclasses = EdFiPipecleanTestBase.__subclasses__()
subclasses += EdFiCompositePipecleanTestBase.__subclasses__()
subclasses.remove(EdFiCompositePipecleanTestBase)
valid_names = set()
valid_names.add(AllDescriptorsPipecleanTest.__name__)
for subclass in subclasses:
    name = subclass.__name__
    valid_names.add(name)
    if len(args) > 0 and name not in args:
        # Skip this class if individual tests have been specified and this
        # isn't one of them
        continue
    EdFiPipecleanTaskSequence.tasks.append(subclass)
# Add descriptor pipeclean tests after resource pipeclean tests
# if it's been named or we're running everything
if len(args) == 0 or AllDescriptorsPipecleanTest.__name__ in args:
    EdFiPipecleanTaskSequence.tasks.append(AllDescriptorsPipecleanTest)

EdFiPipecleanTaskSequence.tasks.append(EdFiPipecleanTestTerminator)


class EdFiPipecleanTestMixin(object):
    host = get_config_value('host')
    min_wait = 2000
    max_wait = 9000


class DummyTaskSet(TaskSet):
    tasks = [lambda *_: None]


# Create a single locust instance containing all added tasks.
# If locust was invoked without arguments, name this EdFiPipecleanTest.
# Otherwise, give it the name of one of the arguments, and create "dummy"
# locusts for the other arguments so locust doesn't complain about missing
# locusts.
exports = []
if len(args) == 0:
    args.append('EdFiPipecleanTest')

for idx, arg in enumerate(args):
    if arg not in valid_names and arg != 'EdFiPipecleanTest':
        continue
    if idx == 0:
        # Use first argument as "real" locust class
        task_set = EdFiPipecleanTaskSequence
    else:
        # Create dummies for others
        task_set = DummyTaskSet
    exports.append(
        type(
            arg,
            (EdFiPipecleanTestMixin, HttpLocust),
            {'task_set': task_set}
        )
    )

# Add all individual pipeclean tests to `locust -f pipeclean_tests.py --list`
if opts.list_commands is True:
    exports.extend([
        type(
            subclass.__name__,
            (EdFiPipecleanTestMixin, HttpLocust),
            {'task_set': DummyTaskSet}
        )
        for subclass in subclasses
    ])

_module = ModuleType(__name__)
for export in exports:
    setattr(_module, export.__name__, export)
sys.modules[__name__] = _module
