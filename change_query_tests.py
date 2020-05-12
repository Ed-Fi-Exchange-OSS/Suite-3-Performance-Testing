"""
This module dynamically imports change-query-testing locusts for all scenarios
registered in the `tasks.change_query` package and combines them into a single
locust which runs each scenario in order.

In order to restrict which scenarios are run, you can name *ChangeQueryTest
classes on the command line in the locust invocation, and only those classes
will be added to the run.

E.g.

`locust -f change_query_tests.py -c 1 --no-web StaffChangeQueryTest StudentChangeQueryTest`
"""
import importlib
import os
import pkgutil
import sys
from types import ModuleType

from locust import HttpLocust, TaskSet
from locust.main import parse_options

from edfi_performance.config import get_config_value
from edfi_performance.tasks.change_query import EdFiChangeQueryTestBase, EdFiChangeQueryTaskSequence, \
    EdFiChangeQueryTestTerminator

# Import modules under tasks.change_query package so *ChangeQueryTest classes are registered
tasks_submodules = [
    name for _, name, _ in pkgutil.iter_modules(
        [os.path.join('edfi_performance', 'tasks', 'change_query')],
        prefix='edfi_performance.tasks.change_query.')
]
for mod_name in tasks_submodules:
    importlib.import_module(mod_name)


# Collect *ChangeQueryTest classes and append them to
# EdFiChangeQueryTaskSequence.tasks
_, opts, args = parse_options()
subclasses = EdFiChangeQueryTestBase.__subclasses__()
valid_names = set()
for subclass in subclasses:
    name = subclass.__name__
    valid_names.add(name)
    if len(args) > 0 and name not in args:
        # Skip this class if individual tests have been specified and this
        # isn't one of them
        continue
    EdFiChangeQueryTaskSequence.tasks.append(subclass)

EdFiChangeQueryTaskSequence.tasks.append(EdFiChangeQueryTestTerminator)


class EdFiChangeQueryTestMixin(object):
    host = get_config_value('host')


class DummyTaskSet(TaskSet):
    tasks = [lambda *_: None]


# Create a single locust instance containing all added tasks.
# If locust was invoked without arguments, name this EdFiChangeQueryTest.
# Otherwise, give it the name of one of the arguments, and create "dummy"
# locusts for the other arguments so locust doesn't complain about missing
# locusts.
exports = []
if len(args) == 0:
    args.append('EdFiChangeQueryTest')

for idx, arg in enumerate(args):
    if arg not in valid_names and arg != 'EdFiChangeQueryTest':
        continue
    if idx == 0:
        # Use first argument as "real" locust class
        task_set = EdFiChangeQueryTaskSequence
    else:
        # Create dummies for others
        task_set = DummyTaskSet
    exports.append(
        type(
            arg,
            (EdFiChangeQueryTestMixin, HttpLocust),
            {'task_set': task_set}
        )
    )

# Add all individual Change Query tests to `locust -f change_query_tests.py --list`
if opts.list_commands is True:
    exports.extend([
        type(
            subclass.__name__,
            (EdFiChangeQueryTestMixin, HttpLocust),
            {'task_set': DummyTaskSet}
        )
        for subclass in subclasses
    ])

_module = ModuleType(__name__)
for export in exports:
    setattr(_module, export.__name__, export)
sys.modules[__name__] = _module
