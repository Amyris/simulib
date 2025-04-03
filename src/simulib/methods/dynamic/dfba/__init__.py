import importlib
import warnings

import simulib.methods.dynamic.dfba.entities as entities

__WARN_NO_DFBA = (
    "could not import dfba - make sure the package"
    " is installed or reinstall simulib with the dfba option: e.g."
    "pip install simulib[dfba]. dFBA simulation will not be available."
)

try:
    dfba_module = importlib.import_module("dfba")
    import simulib.methods.dynamic.dfba.simulator as simulator  # noqa: F401

    __all__ = ("entities", "simulator", "dfba_module")
except (ImportError, ModuleNotFoundError):
    warnings.warn(__WARN_NO_DFBA)
    dfba_module = None
    __all__ = ("entities", "dfba_module")
