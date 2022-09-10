import platform
import sys
import unittest

import pkg_resources

import pyoslog
import pyoslog_test_globals
from pyoslog import core as pyoslog_core

print('Testing pyoslog', pkg_resources.get_distribution('pyoslog').version, 'setup')


class TestSetup(unittest.TestCase):
    def test_constants(self):
        self.assertIsInstance(pyoslog.OS_LOG_DEFAULT, pyoslog_core.os_log_t)
        self.assertEqual(str(pyoslog.OS_LOG_DEFAULT), 'os_log_t(OS_LOG_DEFAULT)')

        self.assertIsInstance(pyoslog.OS_LOG_DISABLED, pyoslog_core.os_log_t)
        self.assertEqual(str(pyoslog.OS_LOG_DISABLED), 'os_log_t(OS_LOG_DISABLED)')

        self.assertEqual(pyoslog.OS_LOG_TYPE_DEFAULT, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEFAULT.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_INFO, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_INFO.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_DEBUG, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEBUG.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_ERROR, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_ERROR.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_FAULT, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_FAULT.value)

    def test_is_supported(self):
        # a little pointless since our platform check and that from is_supported() are identical, but no other option
        matching_platform = sys.platform == 'darwin' and sys.version_info >= (3, 0,) and float(
            '.'.join(platform.mac_ver()[0].split('.')[:2])) >= 10.12
        self.assertEqual(matching_platform, pyoslog.is_supported())

    def test_os_log_create(self):
        log = pyoslog.os_log_create(pyoslog_test_globals.LOG_SUBSYSTEM, pyoslog_test_globals.LOG_CATEGORY)
        self.assertIsInstance(log, pyoslog_core.os_log_t)
        self.assertEqual(str(log), 'os_log_t(%s:%s)' % (pyoslog_test_globals.LOG_SUBSYSTEM,
                                                        pyoslog_test_globals.LOG_CATEGORY))

        # PyArg_ParseTuple in _pyoslog.c handles type validation - just ensure a string is required and test boundaries
        self.assertRaises(TypeError, pyoslog.os_log_create, (None, None))
        self.assertRaises(TypeError, pyoslog.os_log_create, (pyoslog_test_globals.LOG_SUBSYSTEM, None))
        self.assertRaises(TypeError, pyoslog.os_log_create, (None, pyoslog_test_globals.LOG_CATEGORY))

        self.assertRaises(TypeError, pyoslog.os_log_create, ('', ''))
        self.assertRaises(TypeError, pyoslog.os_log_create, (pyoslog_test_globals.LOG_SUBSYSTEM, ''))
        self.assertRaises(TypeError, pyoslog.os_log_create, ('', pyoslog_test_globals.LOG_CATEGORY))

        self.assertRaises(TypeError, pyoslog.os_log_create, (250 * 'p', 255 * 'p'))
        self.assertRaises(TypeError, pyoslog.os_log_create, (pyoslog_test_globals.LOG_SUBSYSTEM, 255 * 'p'))
        self.assertRaises(TypeError, pyoslog.os_log_create, (250 * 'p', pyoslog_test_globals.LOG_CATEGORY))


if __name__ == '__main__':
    unittest.main()
