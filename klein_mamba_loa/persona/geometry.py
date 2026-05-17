"""Persona-Geometry basis: orthogonal directions in the persona condition space.

Reference: "The Geometry of Persona" (arXiv 2512.07092). This module exposes a
small builder for an orthogonal basis that is shared with the SPF Loss
(klein_mamba_loa.flow.loss.pgc_dfm). The basis is a learned tensor of shape
(num_personas, dim); orthogonalization is done by either (a) periodic SVD
re-projection during training, or (b) implicit pressure from the SPF Loss
``lambda_ortho`` term.

Option (b) is the default. Option (a) lives under ``reproject_orthogonal``
and is opt-in at training-step granularity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from torch import Tensor


def _require_torch():
    try:
        import torch  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise ImportError("klein_mamba_loa.persona.geometry requires torch.") from exc
    return __import__("torch")


def make_persona_basis(
    num_personas: int,
    dim: int,
    *,
    seed: int | None = None,
    init: str = "orthogonal",
) -> Tensor:
    """Create an initial persona basis of shape ``(num_personas, dim)``.

    Args:
        num_personas: number of persona strata.
        dim: persona embedding dim. Must be >= num_personas for ``init='orthogonal'``.
        seed: optional torch RNG seed.
        init: 'orthogonal' (Householder QR) or 'gaussian' (random N(0,1/dim)).

    Returns:
        a leaf tensor with ``requires_grad=True``.
    """
    if num_personas < 1:
        raise ValueError("num_personas must be >= 1")
    if dim < 1:
        raise ValueError("dim must be >= 1")
    if init == "orthogonal" and dim < num_personas:
        raise ValueError(
            f"orthogonal init requires dim >= num_personas; got dim={dim}, n={num_personas}"
        )

    torch = _require_torch()
    g = torch.Generator()
    if seed is not None:
        g.manual_seed(seed)

    if init == "orthogonal":
        raw = torch.empty(dim, num_personas).normal_(generator=g)
        q, _ = torch.linalg.qr(raw, mode="reduced")
        basis = q.transpose(0, 1).contiguous()
    elif init == "gaussian":
        basis = torch.empty(num_personas, dim).normal_(
            mean=0.0, std=float(dim) ** -0.5, generator=g
        )
    else:
        raise ValueError(f"unknown init: {init!r}")

    basis.requires_grad_(True)
    return basis


def reproject_orthogonal(basis: Tensor) -> Tensor:
    """Project the basis onto the nearest orthonormal matrix via SVD.

    Use sparingly (e.g. every N steps) when the SPF Loss orthogonality term
    alone is insufficient. Note this breaks gradient flow at the projection.
    """
    torch = _require_torch()
    if basis.dim() != 2:
        raise ValueError(f"basis must be 2-D; got {tuple(basis.shape)}")
    with torch.no_grad():
        u, _, vh = torch.linalg.svd(basis, full_matrices=False)
        projected = u @ vh
        basis.copy_(projected)
    return basis
