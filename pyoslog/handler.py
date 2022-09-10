import logging
from typing import Union

from .core import *

# only the Handler itself should be visible when using `from handler import *`
__all__ = ['Handler']


class Handler(logging.Handler):
    """This logging Handler simply forwards all messages to pyoslog"""

    def __init__(self) -> None:
        """Initialise a Handler instance, logging to OS_LOG_DEFAULT at OS_LOG_TYPE_DEFAULT"""
        logging.Handler.__init__(self)

        self._log_object = OS_LOG_DEFAULT
        self._log_type = OS_LOG_TYPE_DEFAULT

    def setLevel(self, level: Union[int, str]) -> None:
        """Sets the log level, mapping logging.<level> to pyoslog.OS_LOG_TYPE_<equivalent level>."""
        super().setLevel(level)  # normalises level Union[int, str] to int

        pyoslog_type = OS_LOG_TYPE_DEFAULT  # logging.NOTSET or unmatched value

        if self.level >= logging.CRITICAL:
            pyoslog_type = OS_LOG_TYPE_FAULT
        elif self.level >= logging.ERROR:
            pyoslog_type = OS_LOG_TYPE_ERROR
        elif self.level >= logging.WARNING:
            pyoslog_type = OS_LOG_TYPE_DEFAULT
        elif self.level >= logging.INFO:
            pyoslog_type = OS_LOG_TYPE_INFO
        elif self.level >= logging.DEBUG:
            pyoslog_type = OS_LOG_TYPE_DEBUG

        self._log_type = pyoslog_type

    # noinspection PyPep8Naming
    def setSubsystem(self, subsystem: str, category: str = 'default') -> None:
        """Sets the subsystem (in reverse DNS notation), and optionally a category to allow further filtering."""
        self._log_object = os_log_create(subsystem, category)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record, sending its contents to pyoslog."""
        os_log_with_type(self._log_object, self._log_type, self.format(record))
