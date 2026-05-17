"""Stratified Persona Flow (SPF) Loss — core S2 implementation.

Internal class name: PGCDisentangledFMLoss
(Persona-Geometry-Conditioned Disentangled Flow Matching).

Formula (provisional, hypothesis stage):

    L_total = E_t[ || v_pred - v_target ||^2 ]                       # FM term
            + lambda_ortho * sum_{i < j} | <P_i, P_j> |^2             # persona orthogonality
            + lambda_cond  * CE(persona_id | <pooled v_pred, P>)      # conditional id recovery

Foundations:
- Transfusion (arXiv 2408.11039)
- The Geometry of Persona (arXiv 2512.07092)
- Disentangled Representation Learning via Flow Matching (arXiv 2602.05214)

Hypothesis-stage formulation. No empirical claim until S3 (3-run loss-curve study,
blueprint section 7) and S4 (small-scale eval).

Design constraints (blueprint section 7, sub-R14 trigger avoidance):
- File length capped at <= 500 lines; helpers live in persona/disentangle.py
- No torch import at module top; torch is required only when the Loss is invoked
- Forward returns a typed SPFLossOutput so callers do not depend on tuple position

Convention notes vs the blueprint draft:
- The orthogonality penalty was originally written `Σ_{i≠j} <P_i,P_j>^2` in the
  blueprint. This implementation uses the equivalent unordered-pair form
  `Σ_{i<j}` so each pair is counted exactly once; effective penalty differs
  from the ordered convention by a factor of 2 (compensate via lambda_ortho).
- The conditional CE term is computed from a basis-projection of the pooled
  v_pred — no external classifier head required. Pass ``persona_id_logits=...``
  to override with an external head. ``detach_basis_for_cond`` is meaningful
  on the internal-projection path and is a no-op on the external path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from torch import Tensor


@dataclass
class SPFLossConfig:
    """Hyperparameters for SPF Loss.

    lambda_ortho:
        weight on the orthogonality penalty between persona basis vectors.
        Typical bootstrap range (S3 study): 1e-3 .. 1e-1.
    lambda_cond:
        weight on the conditional persona-id cross-entropy term.
        Typical range: 1e-2 .. 1.0.
    fm_reduction:
        reduction over the batch axis for the flow-matching term.
        "mean" (default) or "sum".
    detach_basis_for_cond:
        if True (default) and the conditional CE term is computed via the
        internal basis-projection path, the basis is detached before the
        CE so the CE gradient does not pull persona directions toward
        class-discriminative-but-non-orthogonal solutions. No effect when
        the caller supplies persona_id_logits externally.
    eps:
        numerical floor for divisions / norms.
    """

    lambda_ortho: float = 1e-2
    lambda_cond: float = 1e-1
    fm_reduction: str = "mean"
    detach_basis_for_cond: bool = True
    eps: float = 1e-8

    def __post_init__(self) -> None:
        if self.lambda_ortho < 0 or self.lambda_cond < 0:
            raise ValueError("loss weights must be non-negative")
        if self.fm_reduction not in {"mean", "sum"}:
            raise ValueError(f"fm_reduction must be 'mean' or 'sum'; got {self.fm_reduction!r}")
        if self.eps <= 0:
            raise ValueError("eps must be > 0")


@dataclass
class SPFLossOutput:
    """Structured output so downstream code does not depend on tuple order."""

    total: Tensor
    fm_term: Tensor
    ortho_term: Tensor
    cond_term: Tensor
    diagnostics: dict[str, Any] = field(default_factory=dict)


def _require_torch():
    try:
        import torch  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "PGCDisentangledFMLoss requires torch. "
            "Install with `pip install klein-mamba-loa[flow]`."
        ) from exc
    return __import__("torch")


def orthogonality_penalty(
    basis: Tensor,
    *,
    normalize: bool = True,
    eps: float = 1e-8,
) -> Tensor:
    """Strict-upper-triangular Gram penalty for a persona basis.

    Args:
        basis: tensor of shape (num_personas, dim). Rows are persona directions.
        normalize: if True, basis rows are L2-normalized before the Gram product
            so the penalty measures angular non-orthogonality independently of norm.
        eps: numerical floor.

    Returns:
        scalar tensor equal to ``Σ_{i<j} <P_i, P_j>^2`` — each unordered pair
        contributes once. Returns zero when num_personas < 2.
    """
    torch = _require_torch()
    if basis.dim() != 2:
        raise ValueError(f"basis must be 2-D (num_personas, dim); got {tuple(basis.shape)}")
    n = basis.size(0)
    if n < 2:
        return basis.new_zeros(())

    if normalize:
        norms = basis.norm(dim=1, keepdim=True).clamp_min(eps)
        b = basis / norms
    else:
        b = basis

    gram = b @ b.transpose(0, 1)
    return torch.triu(gram.pow(2), diagonal=1).sum()


def _pool_for_cond(v_pred):
    """Pool v_pred to shape (B, dim) for the conditional CE projection.

    Accepts (B, dim), (B, T, dim), or (B, T_1, ..., T_k, dim). Reduces over
    all middle axes by mean.
    """
    if v_pred.dim() < 2:
        raise ValueError(
            f"v_pred must have at least 2 dims (batch, feature); got {tuple(v_pred.shape)}"
        )
    if v_pred.dim() == 2:
        return v_pred
    return v_pred.flatten(1, -2).mean(dim=1)


def _make_nn_module():
    torch_mod = _require_torch()
    nn = torch_mod.nn
    F = torch_mod.nn.functional

    class _Inner(nn.Module):
        def __init__(self, cfg: SPFLossConfig):
            super().__init__()
            self.cfg = cfg

        def forward(
            self,
            v_pred,
            v_target,
            persona_basis,
            persona_id_logits,
            persona_id_target,
        ):
            cfg = self.cfg

            if v_pred.shape != v_target.shape:
                raise ValueError(
                    f"v_pred and v_target shape mismatch: "
                    f"{tuple(v_pred.shape)} vs {tuple(v_target.shape)}"
                )

            diff = v_pred - v_target
            fm = diff.pow(2).flatten(1).sum(dim=1)
            fm_term = fm.mean() if cfg.fm_reduction == "mean" else fm.sum()

            ortho_term = orthogonality_penalty(persona_basis, normalize=True, eps=cfg.eps)

            used_internal_cond = False
            if persona_id_target is None:
                cond_term = v_pred.new_zeros(())
            elif persona_id_logits is not None:
                cond_term = F.cross_entropy(persona_id_logits, persona_id_target)
            else:
                basis_for_cond = (
                    persona_basis.detach() if cfg.detach_basis_for_cond else persona_basis
                )
                v_dim = v_pred.shape[-1]
                if basis_for_cond.shape[1] != v_dim:
                    raise ValueError(
                        f"persona_basis last dim {basis_for_cond.shape[1]} "
                        f"!= v_pred last dim {v_dim}; cannot internally project"
                    )
                pooled = _pool_for_cond(v_pred)
                cond_logits = pooled @ basis_for_cond.transpose(0, 1)
                cond_term = F.cross_entropy(cond_logits, persona_id_target)
                used_internal_cond = True

            total = fm_term + cfg.lambda_ortho * ortho_term + cfg.lambda_cond * cond_term

            with torch_mod.no_grad():
                diag = {
                    "fm_term": float(fm_term.detach()),
                    "ortho_term": float(ortho_term.detach()),
                    "cond_term": float(cond_term.detach()),
                    "lambda_ortho": cfg.lambda_ortho,
                    "lambda_cond": cfg.lambda_cond,
                    "used_internal_cond_head": used_internal_cond,
                }

            return SPFLossOutput(
                total=total,
                fm_term=fm_term,
                ortho_term=ortho_term,
                cond_term=cond_term,
                diagnostics=diag,
            )

    return _Inner


class PGCDisentangledFMLoss:
    """SPF Loss as a callable. Wraps an inner nn.Module lazily.

    The wrapper layer keeps this symbol importable on a CPU-only host that
    has not installed torch (e.g. for `from klein_mamba_loa.flow.loss import
    PGCDisentangledFMLoss` during S0 verification). Invoking the callable
    requires torch at runtime.

    Usage:

        loss_fn = PGCDisentangledFMLoss(SPFLossConfig(lambda_ortho=0.01, lambda_cond=0.1))

        # Internal cond head (no external classifier needed):
        out = loss_fn(v_pred, v_target, persona_basis, persona_id_target=label)

        # External cond head:
        out = loss_fn(
            v_pred, v_target, persona_basis,
            persona_id_logits=ext_logits, persona_id_target=label,
        )

        out.total.backward()

    The loss has no learnable parameters of its own; the persona basis and
    any external cond head are owned by the caller. ``parameters()`` therefore
    returns an empty iterator.
    """

    def __init__(self, config: SPFLossConfig | None = None):
        self.config = config or SPFLossConfig()
        self._module = None

    def _module_(self):
        if self._module is None:
            inner_cls = _make_nn_module()
            self._module = inner_cls(self.config)
        return self._module

    def __call__(
        self,
        v_pred,
        v_target,
        persona_basis,
        persona_id_logits=None,
        persona_id_target=None,
    ) -> SPFLossOutput:
        return self._module_().forward(
            v_pred=v_pred,
            v_target=v_target,
            persona_basis=persona_basis,
            persona_id_logits=persona_id_logits,
            persona_id_target=persona_id_target,
        )

    def parameters(self):
        return self._module_().parameters()

    def state_dict(self):
        return self._module_().state_dict()

    def load_state_dict(self, sd):
        return self._module_().load_state_dict(sd)
