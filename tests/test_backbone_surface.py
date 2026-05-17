"""Tests for klein_mamba_loa.backbone surface."""

from __future__ import annotations

import pytest


def test_backbone_symbols_importable():
    """Importing the backbone surface must not require torch."""
    from klein_mamba_loa.backbone import (
        BridgeConfig,
        Flux2KleinBackbone,
        Flux2KleinConfig,
        JanusProBackbone,
        JanusProConfig,
        Mamba2Backbone,
        Mamba2Config,
        MambaTransfusionBridge,
    )

    assert MambaTransfusionBridge is not None
    assert BridgeConfig(mamba_dim=16, head_dim=32).num_strata == 4
    assert Mamba2Config().model_id.startswith("state-spaces/mamba")
    assert Flux2KleinConfig().repo_id.startswith("black-forest-labs/")
    assert JanusProConfig().repo_id.startswith("deepseek-ai/")
    # Instantiation is safe; .load() / .__call__() raise NotImplementedError.
    Mamba2Backbone()
    Flux2KleinBackbone()
    JanusProBackbone()


def test_backbone_load_methods_are_not_implemented_yet():
    from klein_mamba_loa.backbone import (
        Flux2KleinBackbone,
        JanusProBackbone,
        Mamba2Backbone,
    )

    for cls in (Mamba2Backbone, Flux2KleinBackbone, JanusProBackbone):
        with pytest.raises(NotImplementedError):
            cls().load()
