from .compatibility import is_supported

if is_supported():
    from .core import *
    from .handler import *

    # remove globals so they are not revealed to importers
    del core  # type: ignore
    del handler  # type: ignore

    del py_object
    del os_log_t
    del Any

del compatibility  # type: ignore
