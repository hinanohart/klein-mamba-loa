"""Tests for the code-layer right-to-be-forgotten endpoint."""

from __future__ import annotations

import pytest

from klein_mamba_loa.persona.erasure import erase_persona


def test_erase_persona_dry_run_returns_plan(tmp_path):
    target = tmp_path / "lora_pool" / "dixie"
    target.mkdir(parents=True)
    (target / "rank8.safetensors").write_bytes(b"\x00" * 16)
    plan = erase_persona("dixie", weights_root=tmp_path / "lora_pool", dry_run=True)
    assert plan.persona_id == "dixie"
    assert plan.dry_run is True
    assert plan.executed is False
    assert plan.mem0_namespace == "persona:dixie"
    assert any(p.name == "rank8.safetensors" for p in plan.lora_paths)
    assert (target / "rank8.safetensors").exists()


def test_erase_persona_executes_and_removes_lora(tmp_path):
    target = tmp_path / "lora_pool" / "wintermute"
    target.mkdir(parents=True)
    (target / "rank16.safetensors").write_bytes(b"\x00" * 32)
    plan = erase_persona("wintermute", weights_root=tmp_path / "lora_pool", dry_run=False)
    assert plan.executed is True
    assert not (target / "rank16.safetensors").exists()


@pytest.mark.parametrize("bad", ["", "../escape", "./hidden", "a/b"])
def test_erase_persona_rejects_invalid_ids(bad):
    with pytest.raises(ValueError):
        erase_persona(bad, dry_run=True)


def test_erase_persona_no_op_when_pool_absent(tmp_path):
    plan = erase_persona("never-loaded", weights_root=tmp_path / "missing", dry_run=False)
    assert plan.executed is True
    assert plan.lora_paths == []
