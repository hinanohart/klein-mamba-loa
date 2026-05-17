"""Disentangle helpers — angular and norm-aware metrics for the persona basis.

Used by:
- S3 integration toy (orthogonality > 0.7 gate, blueprint section 7)
- S4 eval (disentangle metric)
- the SPF Loss for the optional ``normalize=True`` path
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from torch import Tensor


def _require_torch():
    try:
        import torch  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise ImportError("klein_mamba_loa.persona.disentangle requires torch.") from exc
    return __import__("torch")


def angular_orthogonality(basis: Tensor, *, eps: float = 1e-8) -> float:
    """Average ``1 - |cos(P_i, P_j)|`` over all distinct (i, j) pairs.

    1.0 = perfectly orthogonal; 0.0 = collinear. Used as the S3 gate metric.
    """
    torch = _require_torch()
    if basis.dim() != 2:
        raise ValueError(f"basis must be 2-D; got {tuple(basis.shape)}")
    n = basis.size(0)
    if n < 2:
        return 1.0
    norms = basis.norm(dim=1, keepdim=True).clamp_min(eps)
    b = basis / norms
    gram = (b @ b.transpose(0, 1)).abs()
    off = gram - torch.eye(n, device=gram.device, dtype=gram.dtype)
    avg_abs_cos = off.sum() / (n * (n - 1))
    return float(1.0 - avg_abs_cos.detach().cpu())
