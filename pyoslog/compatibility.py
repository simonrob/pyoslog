import os
import platform
import sys


def is_supported() -> bool:
    """Unified logging is only present in macOS 10.12 and later, but it is nicer to not have to check OS type or version
    strings when installing or importing the module - use this method at runtime to check whether it is supported. It is
    important to note that if is_supported() is `False` then none of the module's other methods/constants will exist."""
    supported = sys.platform == 'darwin' and sys.version_info >= (3, 0,) and float(
        '.'.join(platform.mac_ver()[0].split('.')[:2])) >= 10.12
    if not supported and os.environ.get('PYOSLOG_OVERRIDE_IS_SUPPORTED', ''):
        print('Warning: overriding is_supported() on an unsupported platform (use to build documentation only)')
        return True
    return supported
