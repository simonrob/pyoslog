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

print('Testing pyoslog', packaging.version.Version(importlib_metadata.version('pyoslog')), 'logging')


class TestLogging(unittest.TestCase):
    def setUp(self):
        supported_macos = float('.'.join(platform.mac_ver()[0].split('.')[:2])) >= 12
        try:
            import OSLog
            if not supported_macos:
                raise ImportError('unsupported macOS version for testing')
        except ImportError:
            if pyoslog.is_supported() and supported_macos:
                skip_reason = 'Warning: cannot import pyobjc\'s OSLog; unable to run tests (run `pip install ' \
                              'pyobjc-framework-OSLog`)'
                print(skip_reason)
                raise unittest.SkipTest(skip_reason)
            else:
                skip_reason = 'Warning: pyobjc\'s OSLog is not fully supported on this platform (requires macOS ' \
                              '12+); unable to test os_log output'
                print(skip_reason)
                raise unittest.SkipTest(skip_reason)

        self.log = pyoslog.os_log_create(pyoslog_test_globals.LOG_SUBSYSTEM, pyoslog_test_globals.LOG_CATEGORY)
        self.assertIsInstance(self.log, pyoslog_core.os_log_t)
        self.assertEqual(str(self.log), '<os_log_t (%s:%s)>' % (pyoslog_test_globals.LOG_SUBSYSTEM,
                                                                pyoslog_test_globals.LOG_CATEGORY))

        # noinspection PyUnresolvedReferences
        log_scope = OSLog.OSLogStoreScope(OSLog.OSLogStoreCurrentProcessIdentifier)
        # noinspection PyUnresolvedReferences
        self.log_store, error = OSLog.OSLogStore.storeWithScope_error_(log_scope, None)
        self.assertIsNone(error)

    def test_os_log_type_enabled(self):
        # PyArg_ParseTuple in _pyoslog.c handles type validation - just ensure objects are required and test boundaries
        for invalid_object in pyoslog_test_globals.INVALID_LOG_OBJECTS:
            for invalid_type in pyoslog_test_globals.INVALID_LOG_TYPES:
                self.assertRaises(TypeError, pyoslog.os_log_type_enabled, (invalid_object, invalid_type))
        for invalid_object in pyoslog_test_globals.INVALID_LOG_OBJECTS:
            for log_type in pyoslog_test_globals.TestLogTypes:
                self.assertRaises(TypeError, pyoslog.os_log_type_enabled, (invalid_object, log_type.value))
        for log_object in [pyoslog.OS_LOG_DISABLED, pyoslog.OS_LOG_DEFAULT, self.log]:
            for invalid_type in pyoslog_test_globals.INVALID_LOG_TYPES:
                self.assertRaises(TypeError, pyoslog.os_log_type_enabled, (log_object, invalid_type))

        for log_type in pyoslog_test_globals.TestLogTypes:
            self.assertFalse(pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DISABLED, log_type.value))

            # these assertions are pointless, but we can't find the true state any other way, so can't check real values
            default_log_enabled = pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT, log_type.value)
            self.assertEqual(default_log_enabled, default_log_enabled)

            custom_log_enabled = pyoslog.os_log_type_enabled(self.log, log_type.value)
            self.assertEqual(custom_log_enabled, custom_log_enabled)

    def test_os_log_info_enabled(self):
        # note that os_log_info_enabled() just calls os_log_type_enabled - more thorough testing can be found there
        expected_value = pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT,
                                                     pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_INFO.value)
        self.assertEqual(pyoslog.os_log_info_enabled(pyoslog.OS_LOG_DEFAULT), expected_value)

    def test_os_log_debug_enabled(self):
        # note that os_log_debug_enabled() just calls os_log_type_enabled - more thorough testing can be found there
        expected_value = pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT,
                                                     pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEBUG.value)
        self.assertEqual(pyoslog.os_log_debug_enabled(pyoslog.OS_LOG_DEFAULT), expected_value)

    def test_os_log_with_type(self):
        # PyArg_ParseTuple in _pyoslog.c handles type validation - just ensure objects are required and test boundaries
        for invalid_object in pyoslog_test_globals.INVALID_LOG_OBJECTS:
            for invalid_type in pyoslog_test_globals.INVALID_LOG_TYPES:
                sent_message = 'TypeError: %s with type %s' % (invalid_object, invalid_type)
                self.assertRaises(TypeError, pyoslog.os_log_type_enabled, (invalid_object, invalid_type, sent_message))
        for invalid_object in pyoslog_test_globals.INVALID_LOG_OBJECTS:
            for log_type in pyoslog_test_globals.TestLogTypes:
                sent_message = 'TypeError: %s with type 0x%x (%s)' % (invalid_object, log_type.value, log_type)
                self.assertRaises(TypeError, pyoslog.os_log_with_type, (invalid_object, log_type.value, sent_message))
        for log_object in [pyoslog.OS_LOG_DISABLED, pyoslog.OS_LOG_DEFAULT, self.log]:
            for invalid_type in pyoslog_test_globals.INVALID_LOG_TYPES:
                sent_message = 'TypeError: %s with type %s' % (log_object, invalid_type)
                self.assertRaises(TypeError, pyoslog.os_log_type_enabled, (log_object, invalid_type, sent_message))

        for log_type in pyoslog_test_globals.TestLogTypes:
            # get system log configuration via: `sudo log config --status`
            # view via: log stream --predicate 'processImagePath CONTAINS [c] "python"' --style compact --level debug
            sent_message = 'OS_LOG_DEFAULT with type 0x%x (%s)' % (log_type.value, log_type)
            pyoslog.os_log_with_type(pyoslog.OS_LOG_DEFAULT, log_type.value, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)

            # only test types that are enabled - note: starting streaming in Console.app appears to enable all levels,
            # but actually starts "STREAM_LIVE" mode (see `sudo log config --status`) which makes os_log_type_enabled
            # return True for all levels, but doesn't let OSLog retrieve them - as a result, some tests will fail when
            # Console.app is live-streaming logs
            if pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT, log_type.value):
                self.assertIn('_pyoslog', received_message.sender())
                self.assertIn('python', received_message.process().lower())
                self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), log_type)
                self.assertIsNone(received_message.subsystem())
                self.assertIsNone(received_message.category())
                self.assertEqual(received_message.composedMessage(), sent_message)
            else:
                print('Skipped: OS_LOG_DEFAULT tests with disabled type 0x%x (%s)' % (log_type.value, log_type))

            # OS_LOG_DISABLED messages shouldn't appear, so we test the message is the same as the previous one
            sent_message = 'OS_LOG_DISABLED with type 0x%x (%s)' % (log_type.value, log_type)
            pyoslog.os_log_with_type(pyoslog.OS_LOG_DISABLED, log_type.value, sent_message)
            previous_composed_message = received_message.composedMessage()
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
            self.assertEqual(previous_composed_message, received_message.composedMessage())

            # see, e.g.: `log stream --predicate 'subsystem == "ac.robinson.pyoslog"' --style compact --level debug`
            sent_message = 'Custom log object message with type 0x%x (%s)' % (log_type.value, log_type)
            pyoslog.os_log_with_type(self.log, log_type.value, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)

            # new log subsystems inherit the system configuration (which is normally OS_LOG_TYPE_DEFAULT and above)
            # types can be enabled via, e.g., `sudo log config --mode 'level:debug' --subsystem 'ac.robinson.pyoslog'`
            # (but not via Python) and viewed via, e.g., `sudo log config --status --subsystem 'ac.robinson.pyoslog'`
            if pyoslog.os_log_type_enabled(self.log, log_type.value):
                self.assertIn('_pyoslog', received_message.sender())
                self.assertIn('python', received_message.process().lower())
                self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), log_type)
                self.assertEqual(received_message.subsystem(), pyoslog_test_globals.LOG_SUBSYSTEM)
                self.assertEqual(received_message.category(), pyoslog_test_globals.LOG_CATEGORY)
                self.assertEqual(received_message.composedMessage(), sent_message)
            else:
                print('Skipped: custom log object tests with disabled type 0x%x (%s)' % (log_type.value, log_type))

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

    def test_os_log_info(self):
        # note that os_log_info() just calls os_log_with_type - more thorough testing is in test_os_log_with_type
        if pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT, pyoslog.OS_LOG_TYPE_INFO):
            sent_message = 'OS_LOG_DEFAULT with OS_LOG_TYPE_INFO'
            pyoslog.os_log_info(pyoslog.OS_LOG_DEFAULT, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
            self.assertEqual(received_message.composedMessage(), sent_message)
            self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()),
                             pyoslog.OS_LOG_TYPE_INFO)
        else:
            print('Skipped: os_log_info tests with OS_LOG_DEFAULT (type is disabled)')

        if pyoslog.os_log_type_enabled(self.log, pyoslog.OS_LOG_TYPE_INFO):
            sent_message = 'Custom log object with OS_LOG_TYPE_INFO'
            pyoslog.os_log_info(self.log, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
            self.assertEqual(received_message.composedMessage(), sent_message)
            self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()),
                             pyoslog.OS_LOG_TYPE_INFO)
        else:
            print('Skipped: os_log_info tests with custom log object (type is disabled)')

    def test_os_log_debug(self):
        # note that os_log_debug() just calls os_log_with_type - more thorough testing is in test_os_log_with_type
        if pyoslog.os_log_type_enabled(pyoslog.OS_LOG_DEFAULT, pyoslog.OS_LOG_TYPE_DEBUG):
            sent_message = 'OS_LOG_DEFAULT with OS_LOG_TYPE_DEBUG'
            pyoslog.os_log_debug(pyoslog.OS_LOG_DEFAULT, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
            self.assertEqual(received_message.composedMessage(), sent_message)
            self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()),
                             pyoslog.OS_LOG_TYPE_DEBUG)
        else:
            print('Skipped: os_log_debug tests with OS_LOG_DEFAULT (type is disabled)')

        if pyoslog.os_log_type_enabled(self.log, pyoslog.OS_LOG_TYPE_DEBUG):
            sent_message = 'Custom log object with OS_LOG_TYPE_DEBUG'
            pyoslog.os_log_debug(self.log, sent_message)
            received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
            self.assertEqual(received_message.composedMessage(), sent_message)
            self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()),
                             pyoslog.OS_LOG_TYPE_DEBUG)
        else:
            print('Skipped: os_log_debug tests with custom log object (type is disabled)')

    def test_os_log_error(self):
        # note that os_log_error() just calls os_log_with_type - more thorough testing is in test_os_log_with_type
        # (no need to check enabled/disabled - error type messages are always enabled)
        sent_message = 'OS_LOG_DEFAULT with OS_LOG_TYPE_ERROR'
        pyoslog.os_log_error(pyoslog.OS_LOG_DEFAULT, sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_message)
        self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), pyoslog.OS_LOG_TYPE_ERROR)

        sent_message = 'Custom log object with OS_LOG_TYPE_ERROR'
        pyoslog.os_log_error(self.log, sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_message)
        self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), pyoslog.OS_LOG_TYPE_ERROR)

    def test_os_log_fault(self):
        # note that os_log_fault() just calls os_log_with_type - more thorough testing is in test_os_log_with_type
        # (no need to check enabled/disabled - fault type messages are always enabled)
        sent_message = 'OS_LOG_DEFAULT with OS_LOG_TYPE_FAULT'
        pyoslog.os_log_fault(pyoslog.OS_LOG_DEFAULT, sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_message)
        self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), pyoslog.OS_LOG_TYPE_FAULT)

        sent_message = 'Custom log object with OS_LOG_TYPE_FAULT'
        pyoslog.os_log_fault(self.log, sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), sent_message)
        self.assertEqual(pyoslog_test_globals.oslog_level_to_type(received_message.level()), pyoslog.OS_LOG_TYPE_FAULT)

    def test_log(self):
        # note that log() just calls os_log_with_type() - more thorough testing can be found in test_os_log_with_type
        sent_message = 'Shortcut message', 'combining types', -1.0, False, [], (0, 1, 2), {'key': 'value'}, '%{public}s'
        pyoslog.log(*sent_message)
        received_message = pyoslog_test_globals.get_latest_log_message(self.log_store)
        self.assertEqual(received_message.composedMessage(), ' '.join(map(str, sent_message)))

    @unittest.skip('test_strings, used for testing with potentially problematic strings. '
                   'See, e.g., https://github.com/minimaxir/big-list-of-naughty-strings '
                   'or https://github.com/danielmiessler/SecLists if needed')
    def test_strings(self):
        with open('blns.txt') as blns:
            for naughty_string in blns:
                pyoslog.log(naughty_string.rstrip())


if __name__ == '__main__':
    unittest.main()
