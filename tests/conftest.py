from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


def load_module(module_name: str, relative_path: str):
    if module_name in sys.modules:
        return sys.modules[module_name]

    repo_root = Path(__file__).resolve().parents[1]
    file_path = repo_root / relative_path
    spec = spec_from_file_location(module_name, file_path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
