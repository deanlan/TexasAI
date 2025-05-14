"""
"""
from texasgpt import _version
from texasgpt.component import BaseComponent, SystemApp

_CORE_LIBS = ["core"]
_SERVE_LIBS = ["serve"]
_LIBS = _CORE_LIBS + _SERVE_LIBS


__version__ = _version.version

__ALL__ = ["__version__", "SystemApp", "BaseComponent"]


def __getattr__(name: str):
    # Lazy load
    import importlib

    if name in _LIBS:
        return importlib.import_module("." + name, __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
