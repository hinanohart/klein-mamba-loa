"""Tests for the runtime gate (VRAM and run classification)."""

from __future__ import annotations

from klein_mamba_loa.eval.runtime_gate import RuntimeGate, RuntimeGateConfig


def test_vram_in_band_is_green():
    g = RuntimeGate()
    assert g.classify_vram(19.0) == "GREEN"
    assert g.classify_vram(14.5) == "GREEN"
    assert g.classify_vram(23.9) == "GREEN"


def test_vram_above_band_yellow_then_red():
    g = RuntimeGate()
    assert g.classify_vram(25.0) == "YELLOW"
    assert g.classify_vram(30.0) == "RED"


def test_run_loss_must_improve_over_baseline():
    g = RuntimeGate(RuntimeGateConfig(ortho_threshold=0.7))
    assert g.classify_run(final_loss=1.5, baseline_loss=2.0, ortho_metric=0.8) == "GREEN"
    assert g.classify_run(final_loss=2.0, baseline_loss=2.0, ortho_metric=0.9) == "RED"
    assert g.classify_run(final_loss=1.0, baseline_loss=2.0, ortho_metric=0.5) == "YELLOW"
