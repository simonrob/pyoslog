import logging
import platform
import sys
import unittest

import pkg_resources

import pyoslog
import pyoslog_test_globals
from pyoslog import core as pyoslog_core

print('Testing pyoslog', pkg_resources.get_distribution('pyoslog').version, 'handler')


class TestHandler(unittest.TestCase):
    def setUp(self):
        try:
            import OSLog
        except ImportError:
            if pyoslog.is_supported() and float('.'.join(platform.mac_ver()[0].split('.')[:2])) >= 10.15:
                skip_reason = 'Warning: cannot import pyobjc\'s OSLog; unable to run tests (run `pip install ' \
                              'pyobjc-framework-OSLog`)'
                print(skip_reason)
                raise unittest.SkipTest(skip_reason)
            else:
                skip_reason = 'Warning: pyobjc\'s OSLog is not supported on this platform (requires macOS 10.15+); ' \
                              'unable to test logging Handler'
                print(skip_reason)
                raise unittest.SkipTest(skip_reason)

        self.handler = pyoslog.Handler()
        self.assertEqual(self.handler._log_object, pyoslog.OS_LOG_DEFAULT)
        self.assertEqual(self.handler._log_type, pyoslog.OS_LOG_TYPE_DEFAULT)

        # noinspection PyUnresolvedReferences
        log_scope = OSLog.OSLogStoreScope(OSLog.OSLogStoreCurrentProcessIdentifier)
        # noinspection PyUnresolvedReferences
        self.log_store, error = OSLog.OSLogStore.storeWithScope_error_(log_scope, None)
        self.assertIsNone(error)

    def test_setLevel(self):
        for invalid_type in [None, [], (0, 1, 2), {'key': 'value'}]:
            self.assertRaises(TypeError, self.handler.setLevel, invalid_type)

        for level in [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            self.handler.setLevel(level)
            self.assertEqual(self.handler._log_type, pyoslog_test_globals.logging_level_to_type(level))

            self.handler.setLevel(level + 5)  # the logging module allows any positive integers, default 0-50
            self.assertEqual(self.handler._log_type, pyoslog_test_globals.logging_level_to_type(level))

    def test_setSubsystem(self):
        # far more thorough testing is in test_setup.py (setSubsystem essentially duplicates os_log_create)
        self.handler.setSubsystem(pyoslog_test_globals.LOG_SUBSYSTEM, pyoslog_test_globals.LOG_CATEGORY)
        self.assertIsInstance(self.handler._log_object, pyoslog_core.os_log_t)
        self.assertEqual(str(self.handler._log_object), '<os_log_t (%s:%s)>' % (pyoslog_test_globals.LOG_SUBSYSTEM,
                                                                                pyoslog_test_globals.LOG_CATEGORY))

    def test_emit(self):
        # far more thorough testing is in test_logging.py (emit essentially duplicates os_log_with_type)
        sent_record = logging.LogRecord('test', logging.DEBUG, '', 0, 'Handler log message', None, None)
        self.handler.emit(sent_record)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_record.message)


if __name__ == '__main__':
    unittest.main()
