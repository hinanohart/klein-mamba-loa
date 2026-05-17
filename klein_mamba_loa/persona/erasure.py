"""Right-to-be-forgotten endpoint (code-layer ethics gate, default-on).

Exposes ``erase_persona(persona_id, *, dry_run)`` which removes the persona-
specific footprint from the substrates this OSS owns.

Scope guarantees (S1 / S2 boundary explicit):

* **In-tree at S1**: LoRA-pool directory tree under ``weights/lora_pool/<id>/``
  is removed recursively, including non-safetensors residue (configs, logs).
* **NOT yet wired at S1**: Mem0 namespace ``persona:<id>`` cleanup and the
  LightRAG node filter. The adapters live in ``klein_mamba_loa.memory`` and
  are empty surface packages at S1 — ``erase_persona`` returns the intended
  filters in ``ErasurePlan`` but reports their substrate flags as ``False``
  until S2 lands the adapter wiring.

If you need a stronger guarantee right now, run the dry-run, hand the plan to
the operator, and have them delete from Mem0/LightRAG manually. The endpoint
is always callable with ``dry_run=True`` and returns the action plan without
side effects.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

# Strict charset — fs/url safe, no traversal, no NUL/CR/LF.
_PERSONA_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


@dataclass
class ErasurePlan:
    """Outcome of an ``erase_persona`` call.

    ``executed`` is True only when the LoRA-pool deletion completed (or the
    pool dir was absent). ``mem0_cleaned`` and ``lightrag_cleaned`` are
    always False at S1 — they flip to True once the S2 adapters land.
    """

    persona_id: str
    lora_paths: list[Path]
    mem0_namespace: str
    lightrag_filter: dict[str, str] = field(default_factory=dict)
    dry_run: bool = False
    executed: bool = False
    mem0_cleaned: bool = False
    lightrag_cleaned: bool = False
    warnings: list[str] = field(default_factory=list)


def erase_persona(
    persona_id: str,
    *,
    weights_root: Path | None = None,
    dry_run: bool = False,
) -> ErasurePlan:
    """Erase persona-specific weights / adapters.

    Args:
        persona_id: must match ``^[A-Za-z0-9_-]{1,64}$``. Slashes, dots,
            backslashes, control bytes, and absolute paths are rejected.
        weights_root: defaults to ``./weights/lora_pool``.
        dry_run: when True, side-effect free; returns the plan only.

    Returns:
        an ``ErasurePlan`` describing the intended and (when not dry-run)
        executed substrate changes.
    """
    if not _PERSONA_ID_RE.fullmatch(persona_id):
        raise ValueError(f"invalid persona_id {persona_id!r}")

    root = weights_root or Path("weights/lora_pool")
    target_dir = root / persona_id

    # List every file under the persona dir — not just safetensors — so the
    # plan is honest about what cleanup will remove.
    if target_dir.exists():
        lora_paths = sorted(p for p in target_dir.rglob("*") if p.is_file())
    else:
        lora_paths = []

    plan = ErasurePlan(
        persona_id=persona_id,
        lora_paths=lora_paths,
        mem0_namespace=f"persona:{persona_id}",
        lightrag_filter={"persona_id": persona_id},
        dry_run=dry_run,
        executed=False,
        mem0_cleaned=False,
        lightrag_cleaned=False,
        warnings=[
            "mem0-adapter-pending: Mem0 namespace cleanup lands at S2",
            "lightrag-adapter-pending: LightRAG node filter cleanup lands at S2",
        ],
    )

    if dry_run:
        return plan

    if target_dir.exists():
        # rmtree raises on permission/IO error — let the caller see it.
        shutil.rmtree(target_dir)
        if target_dir.exists():
            raise OSError(f"erasure left residue at {target_dir}")

    plan.executed = True
    return plan
