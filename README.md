# Pyoslog
Pyoslog is a simple extension to send messages to the macOS [unified logging system](https://developer.apple.com/documentation/os/os_log) from Python.

```python
from pyoslog import os_log, OS_LOG_DEFAULT
os_log(OS_LOG_DEFAULT, 'Hello from Python!')
```


## Installation
```shell
python -m pip install pyoslog
```

Pyoslog requires macOS 10.12 or later.


## Usage
Pyoslog currently provides the methods [`os_log_create`](https://developer.apple.com/documentation/os/1643744-os_log_create), [`os_log_with_type`](https://developer.apple.com/documentation/os/os_log_with_type) and [`os_log`](https://developer.apple.com/documentation/os/os_log), each with the same signatures as their native versions.

The module also offers a helper method – `log` – that by default posts a message of type `OS_LOG_TYPE_DEFAULT` to `OS_LOG_DEFAULT`. For example, the shortcut `log('message')` is equivalent to `os_log_with_type(OS_LOG_DEFAULT, OS_LOG_TYPE_DEFAULT, 'message')`.

The `Handler` class is designed for use with Python's inbuilt [logging](https://docs.python.org/3/library/logging.html) module.

### Labelling subsystem and category
Create a log object using `os_log_create` and pass it to any of the log methods to add your own subsystem and category labels:

```python
import pyoslog
log = pyoslog.os_log_create('ac.robinson.pyoslog', 'custom-category')
pyoslog.os_log_with_type(log, pyoslog.OS_LOG_TYPE_DEBUG, 'Message to log object', log, 'of type', pyoslog.OS_LOG_TYPE_DEBUG)
```


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


### Receiving log messages
Logs can be viewed using Console.app or the `log` command. For example, messages sent using the default configuration can be monitored using:

```shell
log stream --predicate 'processImagePath CONTAINS "Python"'
```

Messages sent using custom configurations can be filtered more precisely. For example, to receive messages from the labelled subsystem used in the example above:

```shell
log stream --predicate 'subsystem == "ac.robinson.pyoslog"' --level=debug
```

See `man log` for further details about the available options and filters.


## Alternatives
At the time this module was created there were no alternatives available on [PyPi](https://pypi.org/). There are, however, other options available if this is not seen as a constraint:

- [apple_os_log_py](https://github.com/cedar101/apple_os_log_py)
- [pymacoslog](https://github.com/douglas-carmichael/pymacoslog)
- [loggy](https://github.com/pointy-tools/loggy)

Note that the [pyobjc](https://pyobjc.readthedocs.io/) module [OSLog](https://pypi.org/project/pyobjc-framework-OSLog/) is for _reading_ from the unified logging system rather than writing to it. A `log.h` binding is on that project's [roadmap](https://github.com/ronaldoussoren/pyobjc/issues/377), but not yet implemented. 


## License
[Apache 2.0](LICENSE)
