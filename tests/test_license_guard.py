"""Tests for scripts/license_guard.py — RED-license refusal + parser."""

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


def test_canon_pep503_normalises():
    m = _load_module()
    assert m._canon("Flow_Matching") == "flow-matching"
    assert m._canon("flow.matching") == "flow-matching"
    assert m._canon("flow-matching") == "flow-matching"
    assert m._canon("  FLUX.1-dev  ") == "flux-1-dev"


def test_check_passes_on_clean_pyproject():
    m = _load_module()
    rc = m.check()
    assert rc == 0


def test_check_blocks_red_dep_override():
    m = _load_module()
    rc = m.check(red_names={"numpy"})
    assert rc == 1


def test_default_red_names_contain_known_violations():
    m = _load_module()
    red = m._collect_red_names()
    for name in ("flow-matching", "chameleon-7b", "memory-layers-at-scale"):
        assert m._canon(name) in red, f"expected {name!r} in resolved RED set"


def test_parser_lifts_real_notices_entries():
    """REGRESSION GUARD: the previous parser used ``\\*\\*name\\*\\*`` regex,
    but every entry in the real notices file is plain text — so the parser
    returned ``set()`` and the "single source of truth" claim was theatrical.
    This test calls the parser on the actual on-disk notices and asserts
    real-world RED entries are picked up.
    """
    m = _load_module()
    notices = (Path(__file__).resolve().parents[1] / "THIRD_PARTY_NOTICES.md").read_text(
        encoding="utf-8"
    )
    parsed = m._parse_red_from_notices(notices)
    expected_subset = {
        "flow-matching",
        "memory-layers-at-scale",
        "hunyuanvideo",
        "hunyuan3d-2",
        "flux-1-dev",
        "flux-1-kontext-dev",
        "edm2",
        "facebookresearch-flow-matching",
        "facebookresearch-memory",
    }
    missing = expected_subset - parsed
    assert not missing, f"parser missed: {missing}"


def test_parser_handles_both_bullet_styles():
    """Bold-name AND plain-name bullets must both be captured."""
    m = _load_module()
    notices = """\
# Notices

## RED

- **bold-pkg** — license info
- plain-pkg — license info
- alpha/beta — license info
- foo-pkg (alias-name) — license info

## Datasets

- not-red — should be ignored
"""
    parsed = m._parse_red_from_notices(notices)
    assert "bold-pkg" in parsed
    assert "plain-pkg" in parsed
    assert "alpha" in parsed and "beta" in parsed and "alpha-beta" in parsed
    assert "foo-pkg" in parsed and "alias-name" in parsed
    assert "not-red" not in parsed


def test_check_blocks_synthetic_red_from_notices(tmp_path, monkeypatch):
    """End-to-end: add an entry to a synthetic notices file, point the
    guard at it, and confirm a matching dep is rejected."""
    m = _load_module()
    notices = tmp_path / "THIRD_PARTY_NOTICES.md"
    notices.write_text(
        """\
## RED

- evil-pkg — non-commercial license
""",
        encoding="utf-8",
    )
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """\
[project]
name = "x"
version = "0"
dependencies = ["evil-pkg>=1.0"]
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(m, "NOTICES", notices)
    monkeypatch.setattr(m, "PYPROJECT", pyproject)
    rc = m.check()
    assert rc == 1
