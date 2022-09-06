import unittest

import pyoslog
import pyoslog_test_globals


class TestSetup(unittest.TestCase):
    def test_constants(self):
        self.assertEqual(pyoslog.OS_LOG_DEFAULT, 0)

        self.assertEqual(pyoslog.OS_LOG_TYPE_DEFAULT, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEFAULT.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_INFO, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_INFO.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_DEBUG, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_DEBUG.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_ERROR, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_ERROR.value)
        self.assertEqual(pyoslog.OS_LOG_TYPE_FAULT, pyoslog_test_globals.TestLogTypes.OS_LOG_TYPE_FAULT.value)

    def test_os_log_create(self):
        log = pyoslog.os_log_create(pyoslog_test_globals.LOG_SUBSYSTEM, pyoslog_test_globals.LOG_CATEGORY)
        self.assertIsNotNone(log)


if __name__ == '__main__':
    unittest.main()
