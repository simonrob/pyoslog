# Pyoslog
Pyoslog is a simple extension to send messages to the macOS [unified logging system](https://developer.apple.com/documentation/os/os_log) from Python.

```python
from pyoslog import os_log, OS_LOG_DEFAULT
os_log(OS_LOG_DEFAULT, 'Hello from Python!')
```

## Installation
`python -m pip install pyoslog`


## Usage
Pyoslog currently provides the methods [`os_log_create`](https://developer.apple.com/documentation/os/1643744-os_log_create), [`os_log_wih_type`](https://developer.apple.com/documentation/os/os_log_with_type) and [`os_log`](https://developer.apple.com/documentation/os/os_log) with the same signatures as their native versions.

The module also offers a helper method, `log` that by default posts a message of type `OS_LOG_TYPE_DEFAULT` to `OS_LOG_DEFAULT`. For example, the shortcut `pyoslog.log('message')` is equivalent to `pyoslog.os_log_with_type(pyoslog.OS_LOG_DEFAULT, pyoslog.OS_LOG_TYPE_DEFAULT, 'message')`.


### Labelling subsystem and category
Create a log object using `os_log_create` and pass it to any of the log methods to add your own subsystem and category labels:

```python
import pyoslog
log = pyoslog.os_log_create('ac.robinson.pyoslog', 'custom-category')
pyoslog.os_log_with_type(log, pyoslog.OS_LOG_TYPE_DEBUG, 'Message to log object', log, 'of type', pyoslog.OS_LOG_TYPE_DEBUG)
```

### Receiving log messages
Logs can be viewed using Console.app or the `log` command. For example, messages sent using the default configuration can be monitored using:

`log stream --predicate 'processImagePath CONTAINS "Python"'`

Messages sent using custom configurations can be filtered more precisely. For example, to receive messages from the labelled subsystem example above:

`log stream --predicate 'subsystem == "ac.robinson.pyoslog"' --level=debug`


## License
[Apache 2.0](LICENSE)