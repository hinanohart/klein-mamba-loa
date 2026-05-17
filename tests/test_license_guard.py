"""Tests for scripts/license_guard.py — RED-license refusal."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    src = Path(__file__).resolve().parents[1] / "scripts" / "license_guard.py"
    spec = importlib.util.spec_from_file_location("license_guard", src)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["license_guard"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_pkg_name_strips_specifiers():
    m = _load_module()
    assert m._pkg_name("torch>=2.4") == "torch"
    assert m._pkg_name("mem0ai>=0.1") == "mem0ai"
    assert m._pkg_name("flow-matching") == "flow-matching"
    assert m._pkg_name("foo @ https://x/y") == "foo"
    assert m._pkg_name("bar ; python_version<'3.11'") == "bar"
    assert m._pkg_name("klein-mamba-loa[flow]") == "klein-mamba-loa"


def test_check_passes_on_clean_pyproject():
    m = _load_module()
    rc = m.check()
    assert rc == 0


def test_check_blocks_red_dep_override():
    m = _load_module()
    # Simulate a deliberate violation by overriding the RED set with a name
    # actually present in pyproject.toml (we use 'numpy' — guaranteed in core).
    rc = m.check(red_names={"numpy"})
    assert rc == 1


def test_default_red_names_contain_known_violations():
    m = _load_module()
    red = m._collect_red_names()
    for name in ("flow_matching", "chameleon-7b", "memory-layers-at-scale"):
        assert name in red, f"expected {name!r} in resolved RED set"
