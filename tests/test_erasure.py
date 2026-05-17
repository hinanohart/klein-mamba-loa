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
    assert plan.mem0_cleaned is False
    assert plan.lightrag_cleaned is False
    assert any(p.name == "rank8.safetensors" for p in plan.lora_paths)
    assert (target / "rank8.safetensors").exists()


def test_erase_persona_executes_and_removes_lora(tmp_path):
    target = tmp_path / "lora_pool" / "wintermute"
    target.mkdir(parents=True)
    (target / "rank16.safetensors").write_bytes(b"\x00" * 32)
    plan = erase_persona("wintermute", weights_root=tmp_path / "lora_pool", dry_run=False)
    assert plan.executed is True
    assert not (target / "rank16.safetensors").exists()
    assert not target.exists(), "rmtree must remove the persona directory"


def test_erase_persona_removes_non_safetensors_residue(tmp_path):
    """Right-to-be-forgotten must clean up non-LoRA files too."""
    target = tmp_path / "lora_pool" / "neuromancer"
    nested = target / "checkpoints"
    nested.mkdir(parents=True)
    (target / "rank8.safetensors").write_bytes(b"\x00")
    (target / "config.json").write_text("{}")
    (target / "training.log").write_text("step 1\n")
    (nested / "epoch_0.bin").write_bytes(b"\x00")
    plan = erase_persona("neuromancer", weights_root=tmp_path / "lora_pool", dry_run=True)
    names = {p.name for p in plan.lora_paths}
    assert {"rank8.safetensors", "config.json", "training.log", "epoch_0.bin"} <= names

    plan = erase_persona("neuromancer", weights_root=tmp_path / "lora_pool", dry_run=False)
    assert plan.executed is True
    assert not target.exists()


@pytest.mark.parametrize("bad", ["", "../escape", "./hidden", "a/b", "a\\b", "a.b", "x" * 65, "あ"])
def test_erase_persona_rejects_invalid_ids(bad):
    with pytest.raises(ValueError):
        erase_persona(bad, dry_run=True)


def test_erase_persona_no_op_when_pool_absent(tmp_path):
    plan = erase_persona("never-loaded", weights_root=tmp_path / "missing", dry_run=False)
    assert plan.executed is True
    assert plan.lora_paths == []


def test_erase_persona_warnings_disclose_pending_adapters(tmp_path):
    plan = erase_persona("dixie", weights_root=tmp_path / "lora_pool", dry_run=True)
    assert any("mem0-adapter-pending" in w for w in plan.warnings)
    assert any("lightrag-adapter-pending" in w for w in plan.warnings)
