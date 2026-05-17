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
    """Average ``1 - |cos(P_i, P_j)|`` over all unordered distinct pairs.

    Returns a float in ``[0.0, 1.0]``:
    - 1.0 = perfectly orthogonal basis
    - 0.0 = collinear basis

    Used as the S3 gate metric (threshold 0.7 by default; configured in
    klein_mamba_loa.eval.runtime_gate.RuntimeGateConfig).

    Implementation notes:
    - We zero the diagonal explicitly via ``fill_diagonal_`` so the metric
      stays bounded even when a basis row has near-zero norm (clamped to
      ``eps``) and its diagonal Gram entry slips below 1.
    - We average over unordered pairs ``n*(n-1)/2``, matching the
      orthogonality_penalty in pgc_dfm.py (also unordered, ``Σ_{i<j}``).
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
    # Strict-upper triangle keeps each unordered pair exactly once and
    # is unaffected by any drift on the diagonal.
    upper = torch.triu(gram, diagonal=1)
    num_pairs = n * (n - 1) / 2
    avg_abs_cos = upper.sum() / num_pairs
    return float(1.0 - avg_abs_cos.detach().cpu())
