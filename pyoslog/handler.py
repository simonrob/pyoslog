import logging
from typing import Optional

from .core import *

# only the Handler itself should be visible when using `from handler import *`
__all__ = ['Handler']


class Handler(logging.Handler):
    """This logging Handler forwards all messages to pyoslog. The logging level (set as normal via :py:func:`setLevel`)
    is converted to the matching pyoslog.OS_LOG_TYPE_* type, and messages outputted to the unified log."""

    def __init__(
            self, subsystem: Optional[str] = None, category: str = 'default'
    ) -> None:
        """Initialise a Handler instance, logging at OS_LOG_TYPE_DEFAULT

        If a subsystem is provided, a custom os_log object is created using that subsystem.
        If a category is also provided, it will be used; otherwise, 'default' is used as the category name.
        If no subsystem is provided, OS_LOG_DEFAULT is used, and the category parameter is ignored.

        Args:
            subsystem (Optional[str]): The subsystem for os_log (e.g., 'com.example.myapp').
                                       If None, OS_LOG_DEFAULT is used.
            category (Optional[str]): The category for os_log. Used only if subsystem is not None.
                                      Defaults to 'default' if subsystem is provided but category is None.
        """
        logging.Handler.__init__(self)
        self._log_object = OS_LOG_DEFAULT
        if subsystem is not None:
            self.setSubsystem(subsystem, category=category)

    @staticmethod
    def _get_pyoslog_type(level: int) -> int:
        if level >= logging.CRITICAL:
            return OS_LOG_TYPE_FAULT
        elif level >= logging.ERROR:
            return OS_LOG_TYPE_ERROR
        elif level >= logging.WARNING:
            return OS_LOG_TYPE_DEFAULT
        elif level >= logging.INFO:
            return OS_LOG_TYPE_INFO
        elif level >= logging.DEBUG:
            return OS_LOG_TYPE_DEBUG

        return OS_LOG_TYPE_DEFAULT  # logging.NOTSET

    # named to match logging class norms rather than PEP 8 recommendations
    # noinspection PyPep8Naming
    def setSubsystem(self, subsystem: str, category: str = 'default') -> None:
        """Sets the subsystem (typically reverse DNS notation), and optionally a category to allow further filtering."""
        self._log_object = os_log_create(subsystem, category)

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record, sending its contents to pyoslog at a matching level to our own. (note: excluded from built
        documentation as this method is not intended to be called directly.)"""
        os_log_with_type(self._log_object, Handler._get_pyoslog_type(record.levelno), self.format(record))
