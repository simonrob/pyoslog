import logging
from typing import Optional

from .core import *

# only the Handler itself should be visible when using `from handler import *`
__all__ = ['Handler']


class Handler(logging.Handler):
    """This logging Handler forwards all messages to pyoslog. The logging level is converted to the matching
    :py:const:`pyoslog.OS_LOG_TYPE_*` type, and messages outputted to the unified log.

    The default output level is :py:const:`pyoslog.OS_LOG_TYPE_DEFAULT`. This can be configured as normal via
    :py:func:`setLevel`.

    The default output behaviour is to log to :py:const:`pyoslog.OS_LOG_DEFAULT`. This can be configured either by
    calling :py:func:`setSubsystem`, or by providing these arguments when creating a Handler instance."""

    def __init__(self, subsystem: Optional[str] = None, category: str = 'default') -> None:
        """If a subsystem is provided, a custom os_log object is created using that subsystem.
        If a category is also provided, it will be used; otherwise, ``'default'`` is used as the category name.
        If no subsystem is provided, :py:const:`pyoslog.OS_LOG_DEFAULT` is used, and the category parameter is ignored.

        :param subsystem: The subsystem for os_log (e.g., ``'com.example.myapp'``). If subsystem is ``None`` or not
                          provided, :py:const:`pyoslog.OS_LOG_DEFAULT` is used.
        :type subsystem: Optional[str]
        :param category: The category for os_log. Used only if subsystem is not ``None``. Defaults to ``'default'`` if
                         not provided.
        :type category: str = 'default'
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
