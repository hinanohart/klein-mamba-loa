"""LoRA hot-swap pool for persona possession.

S2 stub. The full implementation:
- maps persona_id -> LoRA delta (under ``weights/lora_pool/<persona_id>/``)
- supports atomic possession handoff (MCP persona:// ``possession.atomic``)
- blends two LoRAs by the ``blend`` parameter from the URI query

Until S2 wiring, callers should treat ``LoRAPool.swap_in`` as raising
``NotImplementedError`` while the surface is locked in.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class LoRAHandle:
    persona_id: str
    path: Path
    rank: int


class LoRAPool:
    def __init__(self, weights_root: Path | str = "weights/lora_pool"):
        self.weights_root = Path(weights_root)
        self._loaded: dict[str, LoRAHandle] = {}

    def list_available(self) -> list[str]:
        if not self.weights_root.exists():
            return []
        return sorted(
            p.name for p in self.weights_root.iterdir() if p.is_dir() and not p.name.startswith(".")
        )

    def swap_in(self, persona_id: str, *, atomic: bool = True) -> LoRAHandle:
        raise NotImplementedError("LoRA hot-swap is S2 work; surface locked at this commit.")

    def blend(self, primary_id: str, secondary_id: str, weight: float) -> LoRAHandle:
        raise NotImplementedError("Persona blend is S2 work; surface locked at this commit.")
