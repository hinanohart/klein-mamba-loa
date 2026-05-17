"""FLUX.2 klein 4B FP8 wrapper (surface only; concrete load lands at S2).

Tier1 image generator: ``black-forest-labs/FLUX.2-klein-4b-fp8`` (Apache 2.0,
4.09 GB safetensors, ~8 GB VRAM in FP8). Frozen at training time — only the
LoRA pool is trained.

S1 surface enables:

- ``scripts/measure_vram.py`` import path
- README Tier matrix code-reachable
- S2 wiring to land concrete from_pretrained logic without breaking imports

License audit reference: THIRD_PARTY_NOTICES.md (GREEN row for FLUX.2-klein-4b).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Flux2KleinConfig:
    repo_id: str = "black-forest-labs/FLUX.2-klein-4b-fp8"
    weights_file: str = "flux-2-klein-base-4b-fp8.safetensors"
    dtype: str = "float8_e4m3fn"


class Flux2KleinBackbone:
    def __init__(self, config: Flux2KleinConfig | None = None):
        self.config = config or Flux2KleinConfig()
        self._model = None

    def load(self):
        raise NotImplementedError(
            "Flux2KleinBackbone.load is S2 work; surface only at S1. "
            "See pipeline-state.json next_action for the GPU-host wiring."
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Flux2KleinBackbone forward is S2 work.")
