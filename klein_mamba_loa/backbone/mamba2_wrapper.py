"""Mamba-2 backbone wrapper (surface only; concrete load lands at S2).

Tier1 configuration (24GB single GPU): Mamba-2 1.3B in BF16, ~3GB weights,
state-spaces/mamba checkpoint.

S1 ships only the surface so that:

- ``scripts/measure_vram.py`` can ``from klein_mamba_loa.backbone import``
  the symbol without ImportError on a CPU host.
- The Tier matrix in README is reachable from code (audit gap fix).

S2 lands the real ``load()`` that pulls the checkpoint via huggingface_hub and
freezes parameters (persona LoRA owns trainable params).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Mamba2Config:
    model_id: str = "state-spaces/mamba2-1.3b"
    dtype: str = "bfloat16"
    seq_len: int = 2048


class Mamba2Backbone:
    def __init__(self, config: Mamba2Config | None = None):
        self.config = config or Mamba2Config()
        self._model = None

    def load(self):
        raise NotImplementedError(
            "Mamba2Backbone.load is S2 work; surface only at S1. "
            "Track: experiments/_wip/transfusion-gibson/TODO_NEXT.md P1."
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Mamba2Backbone forward is S2 work.")
