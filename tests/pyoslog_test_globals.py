import enum
import logging

LOG_SUBSYSTEM = 'ac.robinson.pyoslog'
LOG_CATEGORY = 'category'

INVALID_LOG_OBJECTS = [0, '', False, []]
INVALID_LOG_TYPES = [-1, 0x12, '1', False]


class TestLogTypes(enum.IntEnum):
    # see: https://opensource.apple.com/source/xnu/xnu-3789.21.4/libkern/os/log.h.auto.html
    OS_LOG_TYPE_DEFAULT = 0x00
    OS_LOG_TYPE_INFO = 0x01
    OS_LOG_TYPE_DEBUG = 0x02
    OS_LOG_TYPE_ERROR = 0x10
    OS_LOG_TYPE_FAULT = 0x11


def oslog_level_to_type(level):
    # see: https://developer.apple.com/documentation/oslog/oslogentrylog/level
    # int(hex(log_type.value).split('x')[1], 3) + 1 would work, but OS_LOG_TYPE_DEFAULT (0x00) is actually 'notice' (3)
    if level == 0:  # undefined
        return -1  # so tests fail (we never send messages with an undefined type)
    elif level == 1:  # debug
        return TestLogTypes.OS_LOG_TYPE_DEBUG
    elif level == 2:  # info
        return TestLogTypes.OS_LOG_TYPE_INFO
    elif level == 3:  # notice
        return TestLogTypes.OS_LOG_TYPE_DEFAULT
    elif level == 4:  # error
        return TestLogTypes.OS_LOG_TYPE_ERROR
    elif level == 5:  # fault
        return TestLogTypes.OS_LOG_TYPE_FAULT
    return -1


def logging_level_to_type(level):
    if level >= logging.CRITICAL:
        return TestLogTypes.OS_LOG_TYPE_FAULT
    elif level >= logging.ERROR:
        return TestLogTypes.OS_LOG_TYPE_ERROR
    elif level >= logging.WARNING:
        return TestLogTypes.OS_LOG_TYPE_DEFAULT
    elif level >= logging.INFO:
        return TestLogTypes.OS_LOG_TYPE_INFO
    elif level >= logging.DEBUG:
        return TestLogTypes.OS_LOG_TYPE_DEBUG
    return TestLogTypes.OS_LOG_TYPE_DEFAULT


def get_latest_log_message(log_store):
    log_position = log_store.positionWithTimeIntervalSinceEnd_(-10)  # select the last 10 seconds of logs

    # note the 0 for the parameter `options` - reverse (1) would be better for us, but options seem to have no effect
    # log_enumerator_options = OSLog.OSLogEnumeratorOptions(OSLog.OSLogEnumeratorReverse)  # == 1
    enumerator, error = log_store.entriesEnumeratorWithOptions_position_predicate_error_(0, log_position, None, None)
    if error:
        return None  # so tests fail

    # useful properties for us: message.level(), subsystem(), category(), composedMessage() (+ formatString(), date())
    # see: https://github.com/ronaldoussoren/pyobjc/blob/5bc7a29ce8e31fd858c1f1b2796f051a0470d24c/pyobjc-framework-
    #  OSLog/Lib/OSLog/_metadata.py#L51
    # note that we filter out XPC messages because they appear inconsistently before/after our own - this is for
    # verifying message delivery only, and is a trade-off between realistic usage and testability
    recent_messages = enumerator.allObjects()
    filtered_messages = [msg for msg in recent_messages if msg.subsystem() != 'com.apple.xpc']
    if filtered_messages and len(filtered_messages) > 0:
        return filtered_messages[-1]
    return None
