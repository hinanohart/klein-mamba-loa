"""Mem0 + LightRAG adapter surface.

S1 status: **placeholder, with disclosure flow-through**. The
`erase_persona` endpoint in `klein_mamba_loa.persona.erasure` returns
an `ErasurePlan` whose `mem0_cleaned` and `lightrag_cleaned` flags
remain `False` until this package lands at S2.

Operators relying on right-to-be-forgotten today must also delete
from Mem0 / LightRAG manually; `ErasurePlan.warnings` surfaces this
gap on every call.
"""
