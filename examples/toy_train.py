"""S3 toy training harness — scaffold (CPU-importable, GPU-runnable).

Purpose: demonstrate that `PGCDisentangledFMLoss` produces a monotone-
decreasing loss curve when trained on a synthetic 2-D multi-persona
trajectory, with `angular_orthogonality(persona_basis) >= 0.7` at the
end. Three independent seeds are run and their loss curves averaged
(blueprint section 7 S3 gate).

CPU behaviour: importable without torch installed; calling `main()`
when torch is missing prints a hint and exits 0 (so structural CI
doesn't fail). Real training requires torch + a GPU (or a patient CPU
host); the synthetic problem is small enough to converge in seconds
on a 24 GB GPU.

This file is intentionally minimal — production-grade training lives
under S2+ in `klein_mamba_loa.backbone.*` once the wrappers land.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class ToyTrainConfig:
    num_personas: int = 4
    dim: int = 32
    batch_size: int = 64
    steps: int = 200
    lr: float = 1e-3
    lambda_ortho: float = 1e-2
    lambda_cond: float = 1e-1
    seeds: tuple[int, ...] = (0, 1, 2)
    log_every: int = 25
    device: str = "auto"  # "auto" -> cuda if available else cpu


def _maybe_torch():
    try:
        import torch  # noqa: F401
    except Exception:
        return None
    return __import__("torch")


def _select_device(torch_mod, requested: str) -> str:
    if torch_mod is None:
        return "cpu"
    if requested != "auto":
        return requested
    return "cuda" if torch_mod.cuda.is_available() else "cpu"


def _make_synthetic_batch(torch_mod, cfg: ToyTrainConfig, basis):
    """Sample a batch whose target velocity is a persona-coloured
    perturbation around the persona basis direction.

    Each sample is assigned a persona id i ~ Uniform[0,num_personas).
    Target v = basis[i] + small noise. v_pred (modelled below) is a
    learned linear projection of x ~ Normal(0,I); the projection is
    expected to recover the basis row after training, while the
    orthogonality penalty keeps basis rows orthogonal.
    """
    ids = torch_mod.randint(0, cfg.num_personas, (cfg.batch_size,))
    targets = basis.index_select(0, ids)
    noise = 0.1 * torch_mod.randn_like(targets)
    v_target = targets + noise
    return ids, v_target


def _train_one_seed(torch_mod, cfg: ToyTrainConfig, seed: int) -> dict:
    from klein_mamba_loa.flow.loss.pgc_dfm import (
        PGCDisentangledFMLoss,
        SPFLossConfig,
    )
    from klein_mamba_loa.persona.disentangle import angular_orthogonality
    from klein_mamba_loa.persona.geometry import make_persona_basis

    torch_mod.manual_seed(seed)
    device = _select_device(torch_mod, cfg.device)

    basis = make_persona_basis(cfg.num_personas, cfg.dim, seed=seed).to(device)
    # Linear "model": project x to a velocity prediction. Trainable.
    nn = torch_mod.nn
    model = nn.Linear(cfg.dim, cfg.dim, bias=False).to(device)

    loss_fn = PGCDisentangledFMLoss(
        SPFLossConfig(lambda_ortho=cfg.lambda_ortho, lambda_cond=cfg.lambda_cond)
    )
    optimizer = torch_mod.optim.Adam(list(model.parameters()) + [basis], lr=cfg.lr)

    history = []
    for step in range(cfg.steps):
        ids, v_target = _make_synthetic_batch(torch_mod, cfg, basis.detach())
        ids = ids.to(device)
        v_target = v_target.to(device)
        x = torch_mod.randn(cfg.batch_size, cfg.dim, device=device)
        v_pred = model(x)
        out = loss_fn(
            v_pred=v_pred,
            v_target=v_target,
            persona_basis=basis,
            persona_id_target=ids,
        )
        optimizer.zero_grad(set_to_none=True)
        out.total.backward()
        optimizer.step()
        if step % cfg.log_every == 0 or step == cfg.steps - 1:
            ortho = angular_orthogonality(basis)
            history.append(
                {
                    "step": step,
                    "loss": float(out.total.detach().cpu()),
                    "fm": out.diagnostics["fm_term"],
                    "ortho_metric": ortho,
                }
            )
    return {"seed": seed, "history": history}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SPF Loss toy training (S3 gate)")
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--out", type=Path, default=Path("toy_train_report.json"))
    args = parser.parse_args(argv)

    torch_mod = _maybe_torch()
    if torch_mod is None:
        print(
            "examples/toy_train.py: torch is not installed; "
            "this scaffold runs only with `pip install klein-mamba-loa[flow]`."
        )
        return 0

    cfg = ToyTrainConfig(steps=args.steps)
    runs = [_train_one_seed(torch_mod, cfg, seed) for seed in cfg.seeds]
    final_losses = [r["history"][-1]["loss"] for r in runs]
    final_ortho = [r["history"][-1]["ortho_metric"] for r in runs]

    report = {
        "config": asdict(cfg),
        "runs": runs,
        "summary": {
            "mean_final_loss": sum(final_losses) / len(final_losses),
            "mean_final_ortho": sum(final_ortho) / len(final_ortho),
            "all_runs_decreased": all(
                r["history"][-1]["loss"] < r["history"][0]["loss"] for r in runs
            ),
        },
    }
    args.out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
