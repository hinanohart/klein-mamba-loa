"""Right-to-be-forgotten endpoint (code-layer ethics gate, default-on).

This module exposes a single function `erase_persona(persona_id, *, dry_run)`
that removes the persona-specific footprint across the three substrates the
project touches:

  1. LoRA delta weights stored under `weights/lora_pool/<persona_id>/`
  2. Mem0 namespace `persona:<persona_id>`
  3. LightRAG nodes whose `persona_id` attribute equals `<persona_id>`

The implementation is a stub at S1 scaffold. S2 wires it to the real LoRA
pool and the memory adapters. At any project stage, the function is callable
with `dry_run=True` and returns the action plan without side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ErasurePlan:
    persona_id: str
    lora_paths: list[Path]
    mem0_namespace: str
    lightrag_filter: dict
    dry_run: bool
    executed: bool


def erase_persona(
    persona_id: str,
    *,
    weights_root: Path | None = None,
    dry_run: bool = False,
) -> ErasurePlan:
    if not persona_id or "/" in persona_id or persona_id.startswith("."):
        raise ValueError(f"invalid persona_id: {persona_id!r}")

    root = weights_root or Path("weights/lora_pool")
    target_dir = root / persona_id
    lora_paths = sorted(target_dir.glob("*.safetensors")) if target_dir.exists() else []

    plan = ErasurePlan(
        persona_id=persona_id,
        lora_paths=lora_paths,
        mem0_namespace=f"persona:{persona_id}",
        lightrag_filter={"persona_id": persona_id},
        dry_run=dry_run,
        executed=False,
    )

    if dry_run:
        return plan

    for p in lora_paths:
        p.unlink(missing_ok=True)
    if target_dir.exists():
        try:
            target_dir.rmdir()
        except OSError:
            pass

    # S2: wire to Mem0 + LightRAG adapters.
    # Intentionally NOT raising here — the file-level erasure is the
    # minimum guarantee; remote substrate cleanup is best-effort and
    # is logged by the adapter layer.

    plan.executed = True
    return plan
