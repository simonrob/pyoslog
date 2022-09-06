import platform
import sys
import unittest

import pyoslog
import pyoslog_test_globals

import pkg_resources

print('Testing pyoslog', pkg_resources.get_distribution('pyoslog').version)

try:
    import OSLog
except ImportError:
    if pyoslog.is_supported() and float('.'.join(platform.mac_ver()[0].split('.')[:2])) >= 10.15:
        sys.exit('Error: cannot import pyobjc\'s OSLog; unable to run tests (do `pip install pyobjc-framework-OSLog`)')
    else:
        sys.exit('Error: pyobjc\'s OSLog is not supported on this platform (needs macOS 10.15+); unable to test output')


class TestLogging(unittest.TestCase):
    def setUp(self):
        self.log = pyoslog.os_log_create(pyoslog_test_globals.LOG_SUBSYSTEM, pyoslog_test_globals.LOG_CATEGORY)

        # noinspection PyUnresolvedReferences
        log_scope = OSLog.OSLogStoreScope(OSLog.OSLogStoreCurrentProcessIdentifier)
        # noinspection PyUnresolvedReferences
        self.log_store, error = OSLog.OSLogStore.storeWithScope_error_(log_scope, None)
        self.assertIsNone(error)

    def test_os_log_create(self):
        self.assertIsNotNone(self.log)

    def test_os_log_with_type(self):
        for log_type in pyoslog_test_globals.TestLogTypes:
            # view via: log stream --predicate 'processImagePath CONTAINS [c] "python"' --style compact --level debug
            sent_message = 'OS_LOG_DEFAULT with type 0x%x (%s)' % (log_type.value, log_type)
            pyoslog.os_log_with_type(pyoslog.OS_LOG_DEFAULT, log_type.value, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)

            # debug type messages don't appear via the OSLog framework so can't test (but they *are* sent - see Console)
            if log_type != pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEBUG:
                self.assertIn('_pyoslog', received_message.sender())
                self.assertIn('python', received_message.process())
                self.assertEqual(pyoslog_test_globals.level_to_type(received_message.level()), log_type)
                self.assertIsNone(received_message.subsystem())
                self.assertIsNone(received_message.category())
                self.assertEqual(received_message.composedMessage(), sent_message)

            # OS_LOG_DISABLED messages shouldn't appear, so we test the message is the same as the previous one
            sent_message = 'OS_LOG_DISABLED with type 0x%x (%s)' % (log_type.value, log_type)
            pyoslog.os_log_with_type(pyoslog.OS_LOG_DISABLED, log_type.value, sent_message)
            previous_composed_message = received_message.composedMessage()
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
            self.assertEqual(previous_composed_message, received_message.composedMessage())

            # view via, e.g.: log stream --predicate 'subsystem == "ac.robinson.pyoslog"' --style compact --level debug
            sent_message = 'Custom log object message with type 0x%x (%s)' % (log_type.value, log_type)
            pyoslog.os_log_with_type(self.log, log_type.value, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)

            # debug type messages don't appear via the OSLog framework so can't test (but they *are* sent - see Console)
            if log_type != pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEBUG:
                self.assertIn('_pyoslog', received_message.sender())
                self.assertIn('python', received_message.process())
                self.assertEqual(pyoslog_test_globals.level_to_type(received_message.level()), log_type)
                self.assertEqual(received_message.subsystem(), pyoslog_test_globals.LOG_SUBSYSTEM)
                self.assertEqual(received_message.category(), pyoslog_test_globals.LOG_CATEGORY)
                self.assertEqual(received_message.composedMessage(), sent_message)

    def test_os_log(self):
        # note that os_log() just calls os_log_with_type - more thorough testing can be found in test_os_log_with_type
        sent_message = 'OS_LOG_DEFAULT with no type specified'
        pyoslog.os_log(pyoslog.OS_LOG_DEFAULT, sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_message)

        sent_message = 'Custom log object with no type specified'
        pyoslog.os_log(self.log, sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_message)

    def test_log(self):
        # note that log() just calls os_log_with_type() - more thorough testing can be found in test_os_log_with_type
        sent_message = 'Shortcut log message', 'combining types', -1.0, False, (0, 1, 2), {'key': 'value'}, '%{public}s'
        pyoslog.log(*sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), ' '.join(map(str, sent_message)))


if __name__ == '__main__':
    unittest.main()
