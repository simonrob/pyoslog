import _pyoslog

OS_LOG_DEFAULT = _pyoslog.OS_LOG_DEFAULT

OS_LOG_TYPE_DEFAULT = _pyoslog.OS_LOG_TYPE_DEFAULT
OS_LOG_TYPE_INFO = _pyoslog.OS_LOG_TYPE_INFO
OS_LOG_TYPE_DEBUG = _pyoslog.OS_LOG_TYPE_DEBUG
OS_LOG_TYPE_ERROR = _pyoslog.OS_LOG_TYPE_ERROR
OS_LOG_TYPE_FAULT = _pyoslog.OS_LOG_TYPE_FAULT


def os_log_create(subsystem, category):
    """Creates a custom log object. See: https://developer.apple.com/documentation/os/1643744-os_log_create"""
    return _pyoslog.os_log_create(subsystem, category)


def os_log_with_type(log_object, log_type, *message):
    """Sends a message at a specific logging level, such as default, info, debug, error, or fault, to the logging
    system. See: https://developer.apple.com/documentation/os/os_log_with_type"""
    return _pyoslog.os_log_with_type(log_object, log_type, ' '.join(map(str, message)))


def os_log(log_object, *message):
    """Sends a default-level message to the logging system. See: https://developer.apple.com/documentation/os/os_log"""
    return os_log_with_type(log_object, OS_LOG_TYPE_DEFAULT, *message)


def log(*message, log_object=OS_LOG_DEFAULT, log_type=OS_LOG_TYPE_DEFAULT):
    """Equivalent to os_log_with_type(log_object, log_type, *message) with the default log object and type"""
    return os_log_with_type(log_object, log_type, *message)
