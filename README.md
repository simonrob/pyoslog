# Pyoslog
Pyoslog allows you to send messages to the macOS [unified logging system](https://developer.apple.com/documentation/os/os_log) using Python.

```python
from pyoslog import os_log, OS_LOG_DEFAULT
os_log(OS_LOG_DEFAULT, 'Hello from Python!')
```


## Installation
Pyoslog requires macOS 10.12 or later and Python 3.6 or later.
Install using `pip`:

```shell
python -m pip install pyoslog
```

The module will install and import without error on earlier macOS versions, or on unsupported Operating Systems or incompatible Python versions.
Use `pyoslog.is_supported()` if you need to support incompatible environments and want to know at runtime whether to use pyoslog.
Please note that if `is_supported()` returns `False` then none of the module's other methods or constants will exist.


## Usage
Pyoslog currently provides the following methods:
- [`os_log_create`](https://developer.apple.com/documentation/os/1643744-os_log_create)
- [`os_log_type_enabled`](https://developer.apple.com/documentation/os/1643749-os_log_type_enabled) (and [`info`](https://developer.apple.com/documentation/os/os_log_info_enabled)/[`debug`](https://developer.apple.com/documentation/os/os_log_debug_enabled) variants)
- [`os_log_with_type`](https://developer.apple.com/documentation/os/os_log_with_type)
- [`os_log`](https://developer.apple.com/documentation/os/os_log) (and [`info`](https://developer.apple.com/documentation/os/os_log_info)/[`debug`](https://developer.apple.com/documentation/os/os_log_debug)/[`error`](https://developer.apple.com/documentation/os/os_log_error)/[`fault`](https://developer.apple.com/documentation/os/os_log_fault) variants).

All the pyoslog methods have the same signatures as their native versions, _except_ for where a method requires a `format` parameter.
The `os_log` system requires a constant (static) format specifier, and it is not possible to achieve this via Python.
As a result, all instances of format strings use `"%{public}s"`, and all messages are converted to a string before passing to the native methods.

Pyoslog also offers a helper method – `log` – that by default posts a message of type `OS_LOG_TYPE_DEFAULT` to `OS_LOG_DEFAULT`.
For example, the shortcut `log('message')` is equivalent to `os_log_with_type(OS_LOG_DEFAULT, OS_LOG_TYPE_DEFAULT, 'message')`.

The `Handler` class is designed for use with Python's inbuilt [logging](https://docs.python.org/3/library/logging.html) module.
It works as a drop-in replacement for other Handler varieties.

See [pyoslog's method documentation](https://pyoslog.readthedocs.io/en/latest/reference.html) for a full reference. 

### Labelling subsystem and category
Create a log object using `os_log_create` and pass it to any of the log methods to add your own subsystem and category labels:

```python
import pyoslog
log = pyoslog.os_log_create('ac.robinson.pyoslog', 'custom-category')
pyoslog.os_log_with_type(log, pyoslog.OS_LOG_TYPE_DEBUG, 'Message to log object', log, 'of type', pyoslog.OS_LOG_TYPE_DEBUG)
```

### Enabling and disabling log output
Log output can be enabled or disabled globally by switching between the desired log object and `pyoslog.OS_LOG_DISABLED`:

```python
import pyoslog
log = pyoslog.OS_LOG_DEFAULT
pyoslog.os_log(log, 'Log output enabled')
log = pyoslog.OS_LOG_DISABLED
pyoslog.os_log(log, 'Log output disabled')
```

It is also possible to check whether individual log types are enabled for a particular log object:

```python
import pyoslog
pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT, pyoslog.OS_LOG_TYPE_DEBUG)
```

It is not possible to directly set a log object's mode from Python, but see the `config` section of `man log` for documentation about doing this in `sudo` mode.

### Integration with the logging module
Use the pyoslog `Handler` to direct messages to pyoslog:

```python
import logging, pyoslog
logger = logging.getLogger('My app name')
logger.setLevel(logging.DEBUG)
handler = pyoslog.Handler()
handler.setSubsystem('org.example.your-app', 'filter-category')
logger.addHandler(handler)
logger.debug('message')
```

To configure the Handler's output type, use `handler.setLevel` with a level from the logging module.
These are mapped internally to the `OS_LOG_TYPE` values – for example, `handler.setLevel(logging.DEBUG)` will configure the Handler to output messages of type `OS_LOG_TYPE_DEBUG`.

### Receiving log messages
Logs can be viewed using Console.app or the `log` command.
For example, messages sent using the default configuration can be streamed using:

```shell
log stream --predicate 'processImagePath CONTAINS [c] "python"'
```

Messages sent using custom log objects can be filtered more precisely.
For example, to receive messages from the labelled subsystem used in the example above:

```shell
log stream --predicate 'subsystem == "ac.robinson.pyoslog"' --level debug
```

See `man log` for further details about the available options and filters.

### Handling cleanup
When labelling subsystem and category using the native C methods there is a requirement to free the log object after use (using `os_release`).
The pyoslog module handles this for you – there is no need to `del` or release these objects.


## Limitations
As noted above, while the macOS `os_log` API allows use of a format string with many methods, this name is required to be a C string literal.
As a result, pyoslog hardcodes all format strings to `"%{public}s"`.


## Testing
The pyoslog module's tests require the [pyobjc OSLog framework wrappers](https://pypi.org/project/pyobjc-framework-OSLog/) and the [storeWithScope initialiser](https://developer.apple.com/documentation/oslog/oslogstore/3548057-storewithscope) in order to verify output so, as a result, can only be run on macOS 12 or later.

After installing the OSLog wrappers (via `python -m pip install pyobjc-framework-OSLog`), navigate to the [tests](https://github.com/simonrob/pyoslog/tree/main/tests) directory and run:

```shell
python -m unittest
```

All of pyoslog's code is covered by tests, but please note that if Console.app is live-streaming messages, some tests may fail.
See [`test_logging.py`](https://github.com/simonrob/pyoslog/blob/main/tests/test_logging.py#L96) for discussion about why this is the case.


## Alternatives
At the time this module was created there were no alternatives available on [PyPi](https://pypi.org/search/?q=macos+unified+logging&c=Operating+System+%3A%3A+MacOS).
Since then, the [macos-oslog](https://pypi.org/project/macos-oslog/) module has been released, with broadly equivalent functionality to pyoslog, except for the need to manually release the log object.
There is also [os-signpost](https://pypi.org/project/os-signpost/), which uses `cython` to provide the [`OSSignposter`](https://developer.apple.com/documentation/os/ossignposter) API, and could easily be extended to provide `os_log` functionality.

In addition, there are other options available if PyPi access is not seen as a constraint:

- [apple_os_log_py](https://github.com/cedar101/apple_os_log_py)
- [pymacoslog](https://github.com/douglas-carmichael/pymacoslog)
- [loggy](https://github.com/pointy-tools/loggy)

Note that the [pyobjc](https://pyobjc.readthedocs.io/) module [OSLog](https://pypi.org/project/pyobjc-framework-OSLog/) is for _reading_ from the unified logging system rather than writing to it (and as a result is used for testing pyoslog).
A `log.h` binding is on that project's [roadmap](https://github.com/ronaldoussoren/pyobjc/issues/377), but not yet implemented. 


## License
[Apache 2.0](https://github.com/simonrob/pyoslog/blob/main/LICENSE)
