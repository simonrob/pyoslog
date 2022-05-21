""""Send messages to the macOS unified logging system. See: https://developer.apple.com/documentation/os/os_log"""
from .compatibility import is_supported

if is_supported():
    from .core import *
    from .handler import *

del compatibility
