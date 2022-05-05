from .core import *
import logging


class Handler(logging.Handler):
    """This logging Handler simply forwards all messages to pyoslog"""

    def __init__(self):
        """Initialise a Handler instance, logging to OS_LOG_DEFAULT at OS_LOG_TYPE_DEFAULT"""
        logging.Handler.__init__(self)

        self.log_object = OS_LOG_DEFAULT
        self.log_type = OS_LOG_TYPE_DEFAULT

        self._levelToType = {
            logging.CRITICAL: OS_LOG_TYPE_FAULT,
            logging.ERROR: OS_LOG_TYPE_ERROR,
            logging.WARNING: OS_LOG_TYPE_DEFAULT,
            logging.INFO: OS_LOG_TYPE_INFO,
            logging.DEBUG: OS_LOG_TYPE_DEBUG,
            logging.NOTSET: OS_LOG_TYPE_DEFAULT
        }

    def setLevel(self, level):
        """Sets the log level, mapping logging.<level> to pyoslog.OS_LOG_TYPE_<equivalent level>"""
        self.log_type = self._levelToType.get(level)
        super().setLevel(level)

    # noinspection PyPep8Naming
    def setSubsystem(self, subsystem, category='default'):
        """Sets the subsystem (in reverse DNS notation), and optionally a category to allow further filtering"""
        self.log_object = os_log_create(subsystem, category)

    def emit(self, record):
        """Emit a record, sending its contents to pyoslog"""
        os_log_with_type(self.log_object, self.log_type, self.format(record))
