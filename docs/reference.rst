Reference
=========
See `Apple's documentation <https://developer.apple.com/documentation/os/logging?language=objc>`_ for further
information about macOS logging.


Constants
+++++++++

Log objects
------------

.. py:data:: pyoslog.OS_LOG_DEFAULT
    :type: os_log_t
    :value: The shared disabled log.

.. py:data:: pyoslog.OS_LOG_DISABLED
    :type: os_log_t
    :value: The shared default log.

Log levels/types
----------------

.. py:data:: pyoslog.OS_LOG_TYPE_DEBUG
    :type: int
    :value: The debug log level.

.. py:data:: pyoslog.OS_LOG_TYPE_INFO
    :type: int
    :value: The informational log level.

.. py:data:: pyoslog.OS_LOG_TYPE_DEFAULT
    :type: int
    :value: The default log level.

.. py:data:: pyoslog.OS_LOG_TYPE_ERROR
    :type: int
    :value: The error log level.

.. py:data:: pyoslog.OS_LOG_TYPE_FAULT
    :type: int
    :value: The fault log level.


Methods
+++++++

.. automodule:: pyoslog
    :imported-members:
    :members:
    :exclude-members: Handler


Handler
+++++++

.. autoclass:: pyoslog.Handler
    :members:
