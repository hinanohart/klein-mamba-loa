"""Tests for klein_mamba_loa.persona.lora_pool surface."""

from __future__ import annotations

import pytest

from klein_mamba_loa.persona.lora_pool import LoRAHandle, LoRAPool


def test_list_available_empty_when_root_missing(tmp_path):
    pool = LoRAPool(weights_root=tmp_path / "nope")
    assert pool.list_available() == []


def test_list_available_excludes_dotfiles(tmp_path):
    root = tmp_path / "lora_pool"
    (root / "alpha").mkdir(parents=True)
    (root / "beta").mkdir()
    (root / ".cache").mkdir()
    # also create a regular file at root level (must be ignored — only dirs count)
    (root / "stray.txt").write_text("nope")
    pool = LoRAPool(weights_root=root)
    listed = pool.list_available()
    assert listed == ["alpha", "beta"]


def test_lora_handle_dataclass_fields(tmp_path):
    h = LoRAHandle(persona_id="dixie", path=tmp_path / "x", rank=8)
    assert h.persona_id == "dixie"
    assert h.rank == 8


def test_swap_in_and_blend_raise_until_s2():
    pool = LoRAPool()
    with pytest.raises(NotImplementedError):
        pool.swap_in("dixie")
    with pytest.raises(NotImplementedError):
        pool.blend("dixie", "wintermute", weight=0.5)
