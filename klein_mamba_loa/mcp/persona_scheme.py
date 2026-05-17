"""MCP `persona://` resource scheme — version 0.1.0-draft.

URI form:

    persona://<persona_id>[@<namespace>][?rev=<sha256_8>&blend=<float>]

Payload (JSON) shape (informative, validated in S2):

    {
      "persona_id": "...",
      "namespace": "...",
      "rev": "<sha256_8>",
      "consent": {
        "subject_consent_ref": "...",        // missing = WARN, blocks commercial path
        "real_person": false,
        "deadbot": false
      },
      "possession": { "atomic": true },       // 2PC handoff between hosts
      "blend": 0.0,                            // [0,1]
      "loa_capabilities": [...],
      "memory_refs": [...]
    }

The standard track for this scheme is decoupled from the OSS: this
package ships the draft and operates self-contained even if the
upstream MCP spec never accepts the proposal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlparse

SCHEME = "persona"
DRAFT_VERSION = "0.1.0-draft"


@dataclass
class PersonaURI:
    persona_id: str
    namespace: str | None = None
    rev: str | None = None
    blend: float | None = None


@dataclass
class ConsentBlock:
    subject_consent_ref: str | None = None
    real_person: bool = False
    deadbot: bool = False


@dataclass
class PersonaPayload:
    persona_id: str
    namespace: str | None = None
    rev: str | None = None
    consent: ConsentBlock = field(default_factory=ConsentBlock)
    possession_atomic: bool = True
    blend: float = 0.0
    loa_capabilities: list[str] = field(default_factory=list)
    memory_refs: list[str] = field(default_factory=list)


class PersonaURIError(ValueError):
    """Raised when a string does not parse as a valid persona:// URI."""


def parse_uri(uri: str) -> PersonaURI:
    parsed = urlparse(uri)
    if parsed.scheme != SCHEME:
        raise PersonaURIError(f"expected scheme {SCHEME!r}, got {parsed.scheme!r}")

    raw_id = parsed.netloc or parsed.path.lstrip("/")
    namespace: str | None = None
    if "@" in raw_id:
        raw_id, namespace = raw_id.split("@", 1)
    if not raw_id:
        raise PersonaURIError("missing persona_id")

    qs = parse_qs(parsed.query)
    rev = qs.get("rev", [None])[0]
    blend_raw = qs.get("blend", [None])[0]
    blend: float | None = None
    if blend_raw is not None:
        try:
            blend = float(blend_raw)
        except ValueError as exc:
            raise PersonaURIError(f"invalid blend={blend_raw!r}") from exc
        if not 0.0 <= blend <= 1.0:
            raise PersonaURIError(f"blend out of range [0,1]: {blend}")

    return PersonaURI(persona_id=raw_id, namespace=namespace, rev=rev, blend=blend)


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Returns a list of warnings; empty list = OK for inference.

    Hard errors raise. A returned warning containing the substring
    'missing-consent' is the gate that downstream commercial paths
    MUST treat as a BLOCK.
    """
    warnings: list[str] = []
    if "persona_id" not in payload or not payload["persona_id"]:
        raise PersonaURIError("payload missing persona_id")

    consent = payload.get("consent") or {}
    if not isinstance(consent, dict):
        raise PersonaURIError("consent block must be an object")
    if consent.get("real_person") and not consent.get("subject_consent_ref"):
        warnings.append("missing-consent: real_person=true without subject_consent_ref")
    if consent.get("deadbot") and not consent.get("subject_consent_ref"):
        warnings.append("missing-consent: deadbot=true without subject_consent_ref")
    blend = payload.get("blend", 0.0)
    if not isinstance(blend, (int, float)) or not 0.0 <= float(blend) <= 1.0:
        raise PersonaURIError(f"blend out of range [0,1]: {blend!r}")
    return warnings
