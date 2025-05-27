import logging
import platform
import unittest

import packaging.version

try:
    import importlib.metadata as importlib_metadata  # get package version numbers - available in stdlib from python 3.8
except ImportError:
    # noinspection PyUnresolvedReferences
    import importlib_metadata

import pyoslog
import pyoslog_test_globals
from pyoslog import core as pyoslog_core

print('Testing pyoslog', packaging.version.Version(importlib_metadata.version('pyoslog')), 'handler')


class TestHandler(unittest.TestCase):
    def setUp(self):
        tests_supported_macos = float('.'.join(platform.mac_ver()[0].split('.')[:2])) >= 12
        try:
            import OSLog
            if not tests_supported_macos:
                raise ImportError('unsupported macOS version for testing')
        except ImportError:
            if pyoslog.is_supported() and tests_supported_macos:
                skip_reason = 'Warning: cannot import pyobjc\'s OSLog; unable to run tests (run `pip install ' \
                              'pyobjc-framework-OSLog`)'
                print(skip_reason)
                raise unittest.SkipTest(skip_reason)
            else:
                skip_reason = 'Warning: pyobjc\'s OSLog is not fully supported on this platform (requires macOS ' \
                              '12+); unable to test logging Handler'
                print(skip_reason)
                raise unittest.SkipTest(skip_reason)

        subsystem_handler = pyoslog.Handler(subsystem=pyoslog_test_globals.LOG_SUBSYSTEM)
        self.assertIsInstance(subsystem_handler._log_object, pyoslog_core.os_log_t)
        self.assertEqual(str(subsystem_handler._log_object), '<os_log_t (%s:%s)>' % (pyoslog_test_globals.LOG_SUBSYSTEM,
                                                                                     'default'))
        self.assertEqual(subsystem_handler.level, logging.NOTSET)

        category_handler = pyoslog.Handler(subsystem=pyoslog_test_globals.LOG_SUBSYSTEM,
                                           category=pyoslog_test_globals.LOG_CATEGORY)
        self.assertIsInstance(category_handler._log_object, pyoslog_core.os_log_t)
        self.assertEqual(str(category_handler._log_object), '<os_log_t (%s:%s)>' % (pyoslog_test_globals.LOG_SUBSYSTEM,
                                                                                    pyoslog_test_globals.LOG_CATEGORY))
        self.assertEqual(category_handler.level, logging.NOTSET)

        # specifying a category without a subsystem is ignored
        no_subsystem_handler = pyoslog.Handler(category=pyoslog_test_globals.LOG_CATEGORY)
        self.assertEqual(no_subsystem_handler._log_object, pyoslog.OS_LOG_DEFAULT)

        self.handler = pyoslog.Handler()
        self.assertEqual(self.handler._log_object, pyoslog.OS_LOG_DEFAULT)
        self.assertEqual(self.handler.level, logging.NOTSET)

        # far more thorough testing is in test_setup.py (setSubsystem essentially duplicates os_log_create)
        self.handler.setSubsystem(pyoslog_test_globals.LOG_SUBSYSTEM, pyoslog_test_globals.LOG_CATEGORY)
        self.assertIsInstance(self.handler._log_object, pyoslog_core.os_log_t)
        self.assertEqual(str(self.handler._log_object), '<os_log_t (%s:%s)>' % (pyoslog_test_globals.LOG_SUBSYSTEM,
                                                                                pyoslog_test_globals.LOG_CATEGORY))

        self.logger = logging.getLogger('Pyoslog test logger')
        self.logger.addHandler(self.handler)

        # so that we don't receive framework messages (e.g., 'PlugIn CFBundle 0x122f9cf90 </System/Library/Frameworks/
        # OSLog.framework> (framework, loaded) is now unscheduled for unloading')
        self.logger.setLevel(logging.DEBUG)

        # noinspection PyUnresolvedReferences
        log_scope = OSLog.OSLogStoreScope(OSLog.OSLogStoreCurrentProcessIdentifier)
        # noinspection PyUnresolvedReferences
        self.log_store, error = OSLog.OSLogStore.storeWithScope_error_(log_scope, None)
        self.assertIsNone(error)

    def test_emit(self):
        logging_methods = [
            (self.logger.debug, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEBUG),
            (self.logger.info, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_INFO),
            (self.logger.warning, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEFAULT),
            (self.logger.error, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_ERROR),
            (self.logger.critical, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_FAULT)
        ]
        for log_method, log_type in logging_methods:
            sent_message = 'Handler message via %s / 0x%x (%s)' % (log_method, log_type.value, log_type)
            log_method(sent_message)
            # noinspection DuplicatedCode
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)

            # see test_logging.py for further details about this approach
            if pyoslog.os_log_type_enabled(self.handler._log_object, log_type.value):
                self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), log_type)
                self.assertEqual(received_message.subsystem(), pyoslog_test_globals.LOG_SUBSYSTEM)
                self.assertEqual(received_message.category(), pyoslog_test_globals.LOG_CATEGORY)
                self.assertEqual(received_message.composedMessage(), sent_message)
            else:
                print('Skipped: custom log object Handler tests with disabled type 0x%x (%s)' % (
                    log_type.value, log_type))

        sent_message = 'Handler message via logger.exception()'
        self.logger.exception(sent_message, exc_info=False)  # intended to only be called from an exception
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()),
                         pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_ERROR)
        self.assertEqual(received_message.subsystem(), pyoslog_test_globals.LOG_SUBSYSTEM)
        self.assertEqual(received_message.category(), pyoslog_test_globals.LOG_CATEGORY)
        self.assertEqual(received_message.composedMessage(), sent_message)

        # logging.NOTSET should map to OS_LOG_TYPE_DEFAULT (but we don't test output as explained above)
        self.assertEqual(self.handler._get_pyoslog_type(logging.NOTSET),
                         pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEFAULT)

        logging_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        for log_level in logging_levels:
            expected_type = pyoslog_test_globals.logging_level_to_type(log_level)
            sent_message = 'Handler message via logger.log() at level %d / 0x%x (%s)' % (
                log_level, expected_type.value, expected_type)
            self.logger.log(log_level, sent_message)
            # noinspection DuplicatedCode
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)

            # see test_logging.py for further details about this approach
            if pyoslog.os_log_type_enabled(self.handler._log_object, expected_type.value):
                self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), expected_type)
                self.assertEqual(received_message.subsystem(), pyoslog_test_globals.LOG_SUBSYSTEM)
                self.assertEqual(received_message.category(), pyoslog_test_globals.LOG_CATEGORY)
                self.assertEqual(received_message.composedMessage(), sent_message)
            else:
                print('Skipped: custom log object Handler tests with disabled type 0x%x (%s)' % (
                    expected_type.value, expected_type))


if __name__ == '__main__':
    unittest.main()
