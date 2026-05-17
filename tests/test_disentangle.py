"""Tests for klein_mamba_loa.persona.disentangle."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from klein_mamba_loa.persona.disentangle import angular_orthogonality  # noqa: E402


def test_perfectly_orthogonal_returns_one():
    basis = torch.eye(4)
    assert angular_orthogonality(basis) == pytest.approx(1.0, abs=1e-6)


def test_collinear_returns_zero():
    basis = torch.tensor([[1.0, 0.0], [1.0, 0.0]])
    assert angular_orthogonality(basis) == pytest.approx(0.0, abs=1e-6)


def test_single_row_returns_one():
    basis = torch.randn(1, 8)
    assert angular_orthogonality(basis) == 1.0


def test_two_dim_three_persona_bound():
    """Three vectors in 2-D cannot be mutually orthogonal — metric < 1."""
    basis = torch.tensor(
        [
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
        ]
    )
    val = angular_orthogonality(basis)
    assert 0.0 <= val <= 1.0
    assert val < 1.0


def test_rejects_non_2d_basis():
    with pytest.raises(ValueError):
        angular_orthogonality(torch.randn(4))
