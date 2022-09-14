from ctypes import py_object
from typing import Any

try:
    import _pyoslog  # type: ignore
except ImportError:  # pragma: no cover
    # noinspection PyPep8Naming
    class _pyoslog:  # type: ignore
        print('Warning: mocking _pyoslog class on an unsupported platform - use to build documentation only')
        OS_LOG_TYPE_DEFAULT = 0
        OS_LOG_TYPE_INFO = 0
        OS_LOG_TYPE_DEBUG = 0
        OS_LOG_TYPE_ERROR = 0
        OS_LOG_TYPE_FAULT = 0

        @staticmethod
        def _get_os_log_default():
            return None

# noinspection PyProtectedMember
_default_log = _pyoslog._get_os_log_default()
_os_log_t_native_type = py_object


# noinspection PyPep8Naming
class os_log_t:
    def __init__(self, log_object: _os_log_t_native_type, subsystem: str, category: str) -> None:
        self._log_object = log_object
        self._subsystem = subsystem
        self._category = category
        self._description = '<os_log_t (%s:%s)>' % (self._subsystem, self._category)

    def __repr__(self) -> str:
        return self._description


OS_LOG_DEFAULT = os_log_t(_default_log, None, None)  # type: ignore
OS_LOG_DEFAULT._description = '<os_log_t (OS_LOG_DEFAULT)>'

OS_LOG_DISABLED = os_log_t(None, None, None)  # type: ignore
OS_LOG_DISABLED._description = '<os_log_t (OS_LOG_DISABLED)>'

OS_LOG_TYPE_DEFAULT = _pyoslog.OS_LOG_TYPE_DEFAULT  # type: int
OS_LOG_TYPE_INFO = _pyoslog.OS_LOG_TYPE_INFO  # type: int
OS_LOG_TYPE_DEBUG = _pyoslog.OS_LOG_TYPE_DEBUG  # type: int
OS_LOG_TYPE_ERROR = _pyoslog.OS_LOG_TYPE_ERROR  # type: int
OS_LOG_TYPE_FAULT = _pyoslog.OS_LOG_TYPE_FAULT  # type: int


def os_log_create(subsystem: str, category: str) -> os_log_t:
    """Creates a custom log object.
    See the `native method documentation <https://developer.apple.com/documentation/os/1643744-os_log_create>`_."""
    return os_log_t(_pyoslog.os_log_create(subsystem, category), subsystem, category)


def os_log_type_enabled(log_object: os_log_t, log_type: int) -> bool:
    """Returns a `bool` value that indicates whether the log can write messages with the specified log type. See the
    `native method documentation <https://developer.apple.com/documentation/os/1643749-os_log_type_enabled>`__."""
    # noinspection PyProtectedMember
    return _pyoslog.os_log_type_enabled(log_object._log_object, log_type)


def os_log_info_enabled(log_object: os_log_t) -> bool:
    """Returns a `bool` value that indicates whether info-level logging is enabled for a specified log object.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_info_enabled>`__."""
    return os_log_type_enabled(log_object, OS_LOG_TYPE_INFO)


def os_log_debug_enabled(log_object: os_log_t) -> bool:
    """Returns a `bool` value that indicates whether debug-level logging is enabled for a specified log object.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_debug_enabled>`__."""
    return os_log_type_enabled(log_object, OS_LOG_TYPE_DEBUG)


def os_log_with_type(log_object: os_log_t, log_type: int, *message: Any) -> None:
    """Sends a message at a specified level, such as default, info, debug, error or fault, to the logging system.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_with_type>`__."""
    # noinspection PyProtectedMember
    return _pyoslog.os_log_with_type(log_object._log_object, log_type, ' '.join(map(str, message)))


def os_log(log_object: os_log_t, *message: Any) -> None:
    """Sends a default-level message to the logging system.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log>`__."""
    return os_log_with_type(log_object, OS_LOG_TYPE_DEFAULT, *message)


def os_log_info(log_object: os_log_t, *message: Any) -> None:
    """Sends an info-level message to the logging system.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_info>`__."""
    return os_log_with_type(log_object, OS_LOG_TYPE_INFO, *message)


def os_log_debug(log_object: os_log_t, *message: Any) -> None:
    """Sends a debug-level message to the logging system.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_debug>`__."""
    return os_log_with_type(log_object, OS_LOG_TYPE_DEBUG, *message)


def os_log_error(log_object: os_log_t, *message: Any) -> None:
    """Sends an error-level message to the logging system.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_error>`__."""
    return os_log_with_type(log_object, OS_LOG_TYPE_ERROR, *message)


def os_log_fault(log_object: os_log_t, *message: Any) -> None:
    """Sends a fault-level message to the logging system.
    See the `native method documentation <https://developer.apple.com/documentation/os/os_log_fault>`__."""
    return os_log_with_type(log_object, OS_LOG_TYPE_FAULT, *message)


def log(*message: Any, log_object: os_log_t = OS_LOG_DEFAULT, log_type: int = OS_LOG_TYPE_DEFAULT) -> None:
    """A helper method, equivalent to :py:func:`os_log_with_type` with :py:const:`pyoslog.OS_LOG_DEFAULT` and
    :py:const:`pyoslog.OS_LOG_TYPE_DEFAULT`, but with default keyword arguments for convenience."""
    return os_log_with_type(log_object, log_type, *message)
