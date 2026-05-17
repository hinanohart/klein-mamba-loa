"""Serving surface — commercial-gate, sglang/vllm integration (S2+).

Only the commercial-gate ships at S1. sglang / vllm wiring lands at S2.
"""

from klein_mamba_loa.serving.commercial_gate import (
    CommercialDeploymentBlocked,
    assert_commercial_ready,
)

__all__ = ["CommercialDeploymentBlocked", "assert_commercial_ready"]
