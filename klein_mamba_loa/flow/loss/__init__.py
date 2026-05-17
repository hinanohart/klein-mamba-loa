"""SPF Loss module — Stratified Persona Flow loss for disentangled velocity fields."""

from klein_mamba_loa.flow.loss.pgc_dfm import (
    PGCDisentangledFMLoss,
    SPFLossConfig,
    SPFLossOutput,
    orthogonality_penalty,
)

__all__ = [
    "PGCDisentangledFMLoss",
    "SPFLossConfig",
    "SPFLossOutput",
    "orthogonality_penalty",
]
