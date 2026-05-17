"""MCP `persona://` resource scheme — version 0.1.0-draft.

URI form:

    persona://<persona_id>[@<namespace>][?rev=<sha256_8>&blend=<float>]

Payload (JSON) shape (informative, validated below):

    {
      "persona_id": "...",
      "namespace": "...",
      "rev": "<sha256_8>",                     // 8-hex prefix of weights-bundle sha256
      "consent": {
        "subject_consent_ref": "...",          // missing = WARN, blocks commercial path
        "real_person": false,
        "deadbot": false
      },
      "possession": { "atomic": true },        // 2PC handoff between hosts
      "blend": 0.0,                            // [0,1]
      "loa_capabilities": [...],
      "memory_refs": [...]
    }

The standard track for this scheme is decoupled from the OSS: this package
ships the draft and operates self-contained even if the upstream MCP spec
never accepts the proposal.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlparse

SCHEME = "persona"
DRAFT_VERSION = "0.1.0-draft"

# 8-char prefix of a hex sha256 digest.
_REV_RE = re.compile(r"^[0-9a-fA-F]{8}$")
# Allowed persona_id charset — keep strict for fs/url safety.
_PERSONA_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
# Namespace allows dots (e.g. "team.alpha").
_NAMESPACE_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


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


def _check_persona_id(pid: str) -> None:
    if not _PERSONA_ID_RE.fullmatch(pid):
        raise PersonaURIError(f"invalid persona_id {pid!r}: must match {_PERSONA_ID_RE.pattern}")


def _check_namespace(ns: str) -> None:
    if not _NAMESPACE_RE.fullmatch(ns):
        raise PersonaURIError(f"invalid namespace {ns!r}: must match {_NAMESPACE_RE.pattern}")


def _check_rev(rev: str) -> None:
    if not _REV_RE.fullmatch(rev):
        raise PersonaURIError(f"invalid rev {rev!r}: expected 8-hex sha256 prefix")


def parse_uri(uri: str) -> PersonaURI:
    parsed = urlparse(uri)
    if parsed.scheme != SCHEME:
        raise PersonaURIError(f"expected scheme {SCHEME!r}, got {parsed.scheme!r}")

    raw_id = parsed.netloc or parsed.path.lstrip("/")
    # `persona://x/y` would silently drop `/y` — reject explicitly.
    if parsed.netloc and parsed.path and parsed.path != "":
        raise PersonaURIError(f"path component not allowed after authority: {parsed.path!r}")

    namespace: str | None = None
    if "@" in raw_id:
        raw_id, namespace = raw_id.split("@", 1)
    if not raw_id:
        raise PersonaURIError("missing persona_id")
    _check_persona_id(raw_id)
    if namespace is not None:
        _check_namespace(namespace)

    qs = parse_qs(parsed.query, keep_blank_values=False)
    if any(len(v) != 1 for v in qs.values()):
        raise PersonaURIError(f"each query key must appear at most once; got {dict(qs)!r}")

    rev = qs.get("rev", [None])[0]
    if rev is not None:
        _check_rev(rev)

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
    """Validate a `persona://` JSON payload.

    Returns a list of warnings; empty list means payload is OK for inference.
    Hard schema/format errors raise PersonaURIError. A returned warning whose
    text begins with ``missing-consent`` is the gate that the
    serving/commercial_gate.py BLOCK and that downstream commercial paths
    MUST treat as deployment-blocking.
    """
    warnings: list[str] = []
    if "persona_id" not in payload or not payload["persona_id"]:
        raise PersonaURIError("payload missing persona_id")
    _check_persona_id(payload["persona_id"])

    ns = payload.get("namespace")
    if ns is not None and not isinstance(ns, str):
        raise PersonaURIError("namespace must be str or null")
    if isinstance(ns, str):
        _check_namespace(ns)

    rev = payload.get("rev")
    if rev is not None:
        if not isinstance(rev, str):
            raise PersonaURIError("rev must be str or null")
        _check_rev(rev)

    consent = payload.get("consent") or {}
    if not isinstance(consent, dict):
        raise PersonaURIError("consent block must be an object")
    if consent.get("real_person") and not consent.get("subject_consent_ref"):
        warnings.append("missing-consent: real_person=true without subject_consent_ref")
    if consent.get("deadbot") and not consent.get("subject_consent_ref"):
        warnings.append("missing-consent: deadbot=true without subject_consent_ref")

    possession = payload.get("possession") or {}
    if not isinstance(possession, dict):
        raise PersonaURIError("possession block must be an object")
    if "atomic" in possession and not isinstance(possession["atomic"], bool):
        raise PersonaURIError("possession.atomic must be bool")

    blend = payload.get("blend", 0.0)
    if not isinstance(blend, (int, float)) or not 0.0 <= float(blend) <= 1.0:
        raise PersonaURIError(f"blend out of range [0,1]: {blend!r}")

    caps = payload.get("loa_capabilities", [])
    if not isinstance(caps, list) or not all(isinstance(c, str) for c in caps):
        raise PersonaURIError("loa_capabilities must be list[str]")

    refs = payload.get("memory_refs", [])
    if not isinstance(refs, list) or not all(isinstance(r, str) for r in refs):
        raise PersonaURIError("memory_refs must be list[str]")

    return warnings
