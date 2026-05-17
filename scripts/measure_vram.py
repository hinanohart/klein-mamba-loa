"""S0-c VRAM measurement stub.

Runs a single forward step of the Tier-1 stack and reports
torch.cuda.max_memory_allocated. This is the gate that closes
critic-remainder "VRAM actual measurement" in blueprint section 11.

Usage (on a GPU host):

    python scripts/measure_vram.py --tier 1 --dry-run

In --dry-run mode the model loads are skipped and only the measurement
harness is exercised; this allows structural verification on CPU-only
hosts (e.g. the bootstrap session).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class TierBudget:
    name: str
    vram_gb_target: float
    vram_gb_tolerance: float


TIER_BUDGETS: dict[str, TierBudget] = {
    "0.5": TierBudget(name="Tier0.5", vram_gb_target=11.0, vram_gb_tolerance=2.0),
    "1": TierBudget(name="Tier1", vram_gb_target=19.0, vram_gb_tolerance=5.0),
    "1.5": TierBudget(name="Tier1.5", vram_gb_target=36.0, vram_gb_tolerance=8.0),
}


@dataclass
class Measurement:
    tier: str
    dry_run: bool
    cuda_available: bool
    device_name: str | None
    vram_load_gb: float | None
    vram_after_forward_gb: float | None
    vram_max_allocated_gb: float | None
    forward_seconds: float | None
    budget_target_gb: float
    budget_tolerance_gb: float
    gate: str
    notes: str


def _gate(measured: float | None, budget: TierBudget) -> str:
    if measured is None:
        return "DRY_RUN"
    upper = budget.vram_gb_target + budget.vram_gb_tolerance
    lower = max(0.0, budget.vram_gb_target - budget.vram_gb_tolerance)
    if lower <= measured <= upper:
        return "GREEN"
    if measured > upper * 1.1:
        return "RED"
    return "YELLOW"


def _maybe_import_torch():
    try:
        import torch  # type: ignore
    except Exception:
        return None
    return torch


def _load_stack(tier: str, torch_module):
    """Placeholder. Real loaders land at S1/S2 in:

    - klein_mamba_loa.backbone.flux2_klein_wrapper
    - klein_mamba_loa.backbone.mamba2_wrapper
    - klein_mamba_loa.backbone.mamba_transfusion_bridge

    Until those exist, this raises with a clear message so the
    measurement script never silently passes.
    """
    raise NotImplementedError(
        f"Real Tier-{tier} loaders are S1/S2 work. Use --dry-run for structural verification."
    )


def _run_forward(_model, torch_module) -> float:
    raise NotImplementedError("Real forward harness lands at S2.")


def measure(tier: str, dry_run: bool) -> Measurement:
    budget = TIER_BUDGETS[tier]
    torch_module = _maybe_import_torch()
    cuda_available = bool(torch_module is not None and torch_module.cuda.is_available())
    device_name = torch_module.cuda.get_device_name(0) if cuda_available else None

    if dry_run or not cuda_available:
        return Measurement(
            tier=tier,
            dry_run=dry_run or not cuda_available,
            cuda_available=cuda_available,
            device_name=device_name,
            vram_load_gb=None,
            vram_after_forward_gb=None,
            vram_max_allocated_gb=None,
            forward_seconds=None,
            budget_target_gb=budget.vram_gb_target,
            budget_tolerance_gb=budget.vram_gb_tolerance,
            gate="DRY_RUN",
            notes=(
                "structural verification only; "
                "real measurement requires CUDA host and S2 model loaders"
            ),
        )

    torch_module.cuda.reset_peak_memory_stats()
    model = _load_stack(tier, torch_module)
    load_gb = torch_module.cuda.memory_allocated() / 1024**3

    t0 = time.perf_counter()
    _run_forward(model, torch_module)
    fwd_s = time.perf_counter() - t0

    after_gb = torch_module.cuda.memory_allocated() / 1024**3
    peak_gb = torch_module.cuda.max_memory_allocated() / 1024**3

    return Measurement(
        tier=tier,
        dry_run=False,
        cuda_available=True,
        device_name=device_name,
        vram_load_gb=load_gb,
        vram_after_forward_gb=after_gb,
        vram_max_allocated_gb=peak_gb,
        forward_seconds=fwd_s,
        budget_target_gb=budget.vram_gb_target,
        budget_tolerance_gb=budget.vram_gb_tolerance,
        gate=_gate(peak_gb, budget),
        notes="ok",
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Tier VRAM measurement (S0-c)")
    parser.add_argument("--tier", choices=sorted(TIER_BUDGETS), default="1")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1]
        / "experiments/_wip/transfusion-gibson/vram_report.json",
    )
    args = parser.parse_args(argv)

    m = measure(tier=args.tier, dry_run=args.dry_run)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(asdict(m), indent=2) + "\n")
    print(json.dumps(asdict(m), indent=2))
    return 0 if m.gate in {"GREEN", "DRY_RUN", "YELLOW"} else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
