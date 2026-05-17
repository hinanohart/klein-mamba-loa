"""Regression: examples/toy_train.py must import on a no-torch host.

This guards the disclaimer in the file's docstring (CPU-importable,
GPU-runnable). Running `main()` without torch should print a hint and
return 0; importing the module must never raise.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load():
    src = Path(__file__).resolve().parents[1] / "examples" / "toy_train.py"
    spec = importlib.util.spec_from_file_location("toy_train", src)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["toy_train"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_module_imports_cleanly():
    m = _load()
    assert m.ToyTrainConfig().num_personas == 4


def test_select_device_falls_back_to_cpu_when_no_torch():
    m = _load()
    assert m._select_device(None, "auto") == "cpu"
