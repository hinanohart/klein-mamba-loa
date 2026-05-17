"""Runtime gate — GREEN / YELLOW / RED decision against blueprint section 7 thresholds.

This module is intentionally small and standalone. It is used by:
- scripts/measure_vram.py (S0-c VRAM gate)
- tests/test_runtime_gate.py
- the S3 integration toy harness (3-run loss-curve study)

The S3 gate signature:

    gate.classify_run(final_loss, baseline_loss, ortho_metric)

A run is GREEN iff loss converged below ``baseline_loss - loss_improvement_min``
AND ``angular_orthogonality >= cfg.ortho_threshold`` (default 0.7).

The VRAM gate:

    gate.classify_vram(vram_gb)

    GREEN  when ``|vram_gb - vram_target_gb| <= vram_tolerance_gb``
    RED    when ``vram_gb > 1.1 * (vram_target_gb + vram_tolerance_gb)``
    YELLOW otherwise (including under-provisioning, which is non-fatal but
           warrants a re-budget)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeGateConfig:
    ortho_threshold: float = 0.7
    loss_improvement_min: float = 0.0
    vram_target_gb: float = 19.0
    vram_tolerance_gb: float = 5.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.ortho_threshold <= 1.0:
            raise ValueError(f"ortho_threshold must be in [0,1]; got {self.ortho_threshold}")
        if self.loss_improvement_min < 0:
            raise ValueError(f"loss_improvement_min must be >= 0; got {self.loss_improvement_min}")
        if self.vram_target_gb <= 0:
            raise ValueError(f"vram_target_gb must be > 0; got {self.vram_target_gb}")
        if self.vram_tolerance_gb < 0:
            raise ValueError(f"vram_tolerance_gb must be >= 0; got {self.vram_tolerance_gb}")


class RuntimeGate:
    def __init__(self, config: RuntimeGateConfig | None = None):
        self.config = config or RuntimeGateConfig()

    def classify_vram(self, vram_gb: float) -> str:
        cfg = self.config
        upper = cfg.vram_target_gb + cfg.vram_tolerance_gb
        lower = max(0.0, cfg.vram_target_gb - cfg.vram_tolerance_gb)
        if lower <= vram_gb <= upper:
            return "GREEN"
        if vram_gb > upper * 1.1:
            return "RED"
        return "YELLOW"

    def classify_run(
        self,
        final_loss: float,
        baseline_loss: float,
        ortho_metric: float,
    ) -> str:
        if final_loss >= baseline_loss - self.config.loss_improvement_min:
            return "RED"
        if ortho_metric < self.config.ortho_threshold:
            return "YELLOW"
        return "GREEN"
