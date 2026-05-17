"""Mamba-2 hidden-state to Transfusion diffusion head adapter.

Critic finding (blueprint section 4): transfusion-pytorch (lucidrains) is
Llama-centric, so a Mamba-2 backbone cannot connect to its diffusion head
without an adapter. This module owns that contract.

Stub at S1. Concrete forward lands at S2 immediately before the SPF Loss
integration toy. The interface is:

    bridge = MambaTransfusionBridge(mamba_dim, head_dim, num_strata)
    head_input = bridge(mamba_hidden_state, persona_basis_row)
    v_pred = diffusion_head(head_input, t)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BridgeConfig:
    mamba_dim: int
    head_dim: int
    num_strata: int = 4
    use_layernorm: bool = True


class MambaTransfusionBridge:
    def __init__(self, config: BridgeConfig):
        self.config = config

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(
            "Mamba-Transfusion bridge concrete forward lands at S2; surface only at S1."
        )
