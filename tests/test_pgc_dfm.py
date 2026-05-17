"""Tests for the SPF Loss core (klein_mamba_loa.flow.loss.pgc_dfm).

These tests need torch, so they skip cleanly when torch is unavailable
(the no-torch CI path still imports the symbols below — only the runtime
checks gate on torch).
"""

from __future__ import annotations

import math

import pytest

torch = pytest.importorskip("torch")

from klein_mamba_loa.flow.loss.pgc_dfm import (  # noqa: E402
    PGCDisentangledFMLoss,
    SPFLossConfig,
    orthogonality_penalty,
)


def test_orthogonality_penalty_zero_for_identity_basis():
    basis = torch.eye(4)
    pen = orthogonality_penalty(basis)
    assert float(pen) == pytest.approx(0.0, abs=1e-7)


def test_orthogonality_penalty_nonzero_for_collinear_basis():
    basis = torch.tensor([[1.0, 0.0], [1.0, 0.0]])
    pen = orthogonality_penalty(basis)
    # Both rows are unit and identical → off-diag = 1 → upper triangle = 1.
    assert float(pen) == pytest.approx(1.0, abs=1e-7)


def test_orthogonality_penalty_zero_for_single_row():
    basis = torch.randn(1, 8)
    assert float(orthogonality_penalty(basis)) == 0.0


def test_spf_loss_config_rejects_invalid():
    with pytest.raises(ValueError):
        SPFLossConfig(lambda_ortho=-1.0)
    with pytest.raises(ValueError):
        SPFLossConfig(fm_reduction="none")
    with pytest.raises(ValueError):
        SPFLossConfig(eps=0.0)


def test_loss_runs_with_internal_cond_head():
    cfg = SPFLossConfig(lambda_ortho=1e-2, lambda_cond=1e-1)
    loss_fn = PGCDisentangledFMLoss(cfg)
    n, dim, b = 4, 8, 5
    basis = torch.randn(n, dim, requires_grad=True)
    v_pred = torch.randn(b, dim, requires_grad=True)
    v_target = torch.randn(b, dim)
    labels = torch.randint(0, n, (b,))
    out = loss_fn(v_pred, v_target, basis, persona_id_target=labels)
    assert math.isfinite(float(out.total.detach()))
    assert out.diagnostics["used_internal_cond_head"] is True
    out.total.backward()
    assert basis.grad is not None
    assert v_pred.grad is not None


def test_loss_runs_with_external_cond_head():
    cfg = SPFLossConfig(lambda_ortho=1e-2, lambda_cond=1e-1)
    loss_fn = PGCDisentangledFMLoss(cfg)
    n, dim, b = 3, 6, 4
    basis = torch.randn(n, dim, requires_grad=True)
    v_pred = torch.randn(b, dim, requires_grad=True)
    v_target = torch.randn(b, dim)
    ext_logits = torch.randn(b, n, requires_grad=True)
    labels = torch.randint(0, n, (b,))
    out = loss_fn(
        v_pred,
        v_target,
        basis,
        persona_id_logits=ext_logits,
        persona_id_target=labels,
    )
    assert out.diagnostics["used_internal_cond_head"] is False
    out.total.backward()
    assert basis.grad is not None
    assert ext_logits.grad is not None


def test_detach_basis_for_cond_blocks_cond_gradient_to_basis():
    # When detach is on, the CE term must not contribute to basis.grad.
    cfg_detached = SPFLossConfig(lambda_ortho=0.0, lambda_cond=1.0, detach_basis_for_cond=True)
    cfg_attached = SPFLossConfig(lambda_ortho=0.0, lambda_cond=1.0, detach_basis_for_cond=False)
    n, dim, b = 3, 4, 2
    labels = torch.randint(0, n, (b,))

    def _grad_norm(detach: bool) -> float:
        cfg = cfg_detached if detach else cfg_attached
        loss_fn = PGCDisentangledFMLoss(cfg)
        basis = torch.randn(n, dim, requires_grad=True)
        v_pred = torch.randn(b, dim, requires_grad=True)
        v_target = torch.randn(b, dim)
        out = loss_fn(v_pred, v_target, basis, persona_id_target=labels)
        # zero the FM contribution — only cond term flows.
        # We weighted lambda_ortho=0 already; subtract the FM term so backward
        # carries only lambda_cond * cond_term.
        scalar = out.total - out.fm_term
        scalar.backward()
        assert basis.grad is not None
        return float(basis.grad.norm())

    g_detached = _grad_norm(True)
    g_attached = _grad_norm(False)
    assert g_detached == pytest.approx(0.0, abs=1e-6)
    assert g_attached > 0.0


def test_loss_raises_on_shape_mismatch():
    loss_fn = PGCDisentangledFMLoss()
    basis = torch.randn(3, 4)
    v_pred = torch.randn(2, 4)
    v_target = torch.randn(2, 5)
    with pytest.raises(ValueError):
        loss_fn(v_pred, v_target, basis, persona_id_target=torch.tensor([0, 1]))
