"""Backbone surface — wrappers for the Tier1 stack components.

All concrete loads land at S2. S1 ships surfaces only so that the audit
trail (scripts/measure_vram, README Tier matrix) does not point at
nonexistent symbols.
"""

from klein_mamba_loa.backbone.flux2_klein_wrapper import Flux2KleinBackbone, Flux2KleinConfig
from klein_mamba_loa.backbone.janus_pro_wrapper import JanusProBackbone, JanusProConfig
from klein_mamba_loa.backbone.mamba2_wrapper import Mamba2Backbone, Mamba2Config
from klein_mamba_loa.backbone.mamba_transfusion_bridge import (
    BridgeConfig,
    MambaTransfusionBridge,
)

__all__ = [
    "BridgeConfig",
    "Flux2KleinBackbone",
    "Flux2KleinConfig",
    "JanusProBackbone",
    "JanusProConfig",
    "Mamba2Backbone",
    "Mamba2Config",
    "MambaTransfusionBridge",
]
