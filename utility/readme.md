# Performance Testing Utilities

Files:

* `generate.py` - used to auto-generate boilerplate code for testing new
  resources (e.g. extensions)
* `generate_lib.py` - helper functions for `generate.py`
* `test_gen_resources.py` - unit tests for some of the helper functions.

The `generate.py` has detailed run instructions in it: `python generate.py` to
view.

The `run.sh` (bash) and `run.bat` (cmd.exe or PowerShell) will activate the
Python virtual environment and install pip requirements for you, and then run
the `python generate.py` command. To execute correctly, run

```bash
./run.sh -m <metadataUrl> -n <namespace> -r <resource>
```

To run the unit tests, call: `pytest test_gen_resources.py`
