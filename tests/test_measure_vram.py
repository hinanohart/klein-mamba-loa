"""Tests for scripts/measure_vram.py — gate classification + dry-run.

The script is loaded by path so it can be exercised without installing
it as a package; this matches how CI invokes it.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_module():
    src = Path(__file__).resolve().parents[1] / "scripts" / "measure_vram.py"
    spec = importlib.util.spec_from_file_location("measure_vram", src)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["measure_vram"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_gate_classifies_dry_run_none():
    m = _load_module()
    budget = m.TIER_BUDGETS["1"]
    assert m._gate(None, budget) == "DRY_RUN"


def test_gate_green_when_within_tolerance():
    m = _load_module()
    budget = m.TIER_BUDGETS["1"]  # target=19, tol=5 → [14, 24]
    assert m._gate(19.0, budget) == "GREEN"
    assert m._gate(14.0, budget) == "GREEN"
    assert m._gate(24.0, budget) == "GREEN"


def test_gate_red_when_overflows_relaxed_band():
    m = _load_module()
    budget = m.TIER_BUDGETS["1"]
    assert m._gate(30.0, budget) == "RED"


def test_gate_yellow_when_slightly_over_or_under():
    m = _load_module()
    budget = m.TIER_BUDGETS["1"]
    assert m._gate(25.0, budget) == "YELLOW"
    assert m._gate(0.0, budget) == "YELLOW"


def test_tier_budgets_cover_all_three_tiers():
    m = _load_module()
    assert {"0.5", "1", "1.5"} <= set(m.TIER_BUDGETS.keys())


def test_main_dry_run_returns_zero(tmp_path):
    m = _load_module()
    rc = m.main(["--tier", "1", "--dry-run", "--out", str(tmp_path / "v.json")])
    assert rc == 0
    assert (tmp_path / "v.json").exists()
