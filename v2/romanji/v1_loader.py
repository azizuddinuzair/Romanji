"""Load v1 modules by file path (v1 has no packages and some names have hyphens).

v1 is read-only. This only imports it; it never writes there.
"""

import importlib.util
import sys
from pathlib import Path

V1_DIR = Path(__file__).resolve().parents[2] / "v1"


def load_v1_module(relative_path, alias):
    """Import v1/<relative_path> as `alias` (cached in sys.modules)."""
    if alias in sys.modules:
        return sys.modules[alias]
    path = V1_DIR / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"v1 module not found: {path}")
    spec = importlib.util.spec_from_file_location(alias, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(alias, None)
        raise
    return module
