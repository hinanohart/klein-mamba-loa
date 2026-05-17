"""Commercial deployment consent gate (policy → code translation).

Blueprint section 6 says the ``consent`` field of a ``persona://`` payload
must BLOCK commercial deployment when ``subject_consent_ref`` is missing
and the persona is flagged ``real_person=true`` or ``deadbot=true``.

``mcp.persona_scheme.validate_payload`` only emits ``missing-consent`` as a
WARNING. This module is the code-layer enforcement that turns that warning
into a hard refusal on the commercial path. Callers wire it at the request
boundary (serving/) before any inference.
"""

from __future__ import annotations

from typing import Any

from klein_mamba_loa.mcp.persona_scheme import validate_payload


class CommercialDeploymentBlocked(Exception):
    """Raised when a commercial deployment receives a payload with
    unresolved ``missing-consent`` warnings."""


def assert_commercial_ready(payload: dict[str, Any]) -> None:
    """Reject commercial-path use when consent is missing.

    On the inference / training paths set ``commercial=False`` (the default
    in callers) and use the warnings list directly. On the commercial
    deployment path call this before dispatching the request.
    """
    warnings = validate_payload(payload)
    blocking = [w for w in warnings if w.startswith("missing-consent")]
    if blocking:
        raise CommercialDeploymentBlocked(
            "Commercial deployment blocked by missing consent reference: " + "; ".join(blocking)
        )
