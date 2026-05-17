"""Tests for klein_mamba_loa.persona.geometry."""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from klein_mamba_loa.persona.geometry import (  # noqa: E402
    make_persona_basis,
    reproject_orthogonal,
)


def test_orthogonal_basis_is_orthonormal():
    basis = make_persona_basis(4, 16, seed=0, init="orthogonal")
    gram = basis @ basis.transpose(0, 1)
    eye = torch.eye(4)
    assert torch.allclose(gram, eye, atol=1e-5)
    assert basis.requires_grad is True


def test_gaussian_basis_is_leaf_with_grad():
    basis = make_persona_basis(3, 5, seed=1, init="gaussian")
    assert basis.requires_grad is True
    assert basis.is_leaf is True


def test_make_persona_basis_rejects_bad_args():
    with pytest.raises(ValueError):
        make_persona_basis(0, 4)
    with pytest.raises(ValueError):
        make_persona_basis(4, 0)
    with pytest.raises(ValueError):
        make_persona_basis(8, 4, init="orthogonal")  # dim < num_personas


def test_reproject_orthogonal_restores_orthonormality():
    basis = make_persona_basis(3, 8, seed=2, init="gaussian")
    with torch.no_grad():
        basis.mul_(2.0)  # drift away from orthonormal
    out = reproject_orthogonal(basis)
    # In-place semantics — same object.
    assert out is basis
    gram = basis @ basis.transpose(0, 1)
    assert torch.allclose(gram, torch.eye(3), atol=1e-5)
    assert basis.requires_grad is True
