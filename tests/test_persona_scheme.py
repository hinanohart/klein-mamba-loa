"""Tests for the MCP persona:// resource scheme (0.1.0-draft)."""

from __future__ import annotations

import pytest

from klein_mamba_loa.mcp.persona_scheme import (
    DRAFT_VERSION,
    SCHEME,
    PersonaURIError,
    parse_uri,
    validate_payload,
)


def test_scheme_constants():
    assert SCHEME == "persona"
    assert DRAFT_VERSION.startswith("0.1.0")


def test_parse_uri_minimal():
    u = parse_uri("persona://dixie-flatline")
    assert u.persona_id == "dixie-flatline"
    assert u.namespace is None
    assert u.rev is None
    assert u.blend is None


def test_parse_uri_with_namespace_and_query():
    u = parse_uri("persona://wintermute@aleph?rev=deadbeef&blend=0.25")
    assert u.persona_id == "wintermute"
    assert u.namespace == "aleph"
    assert u.rev == "deadbeef"
    assert u.blend == pytest.approx(0.25)


def test_parse_uri_rejects_other_scheme():
    with pytest.raises(PersonaURIError):
        parse_uri("https://example.com/dixie")


def test_parse_uri_rejects_missing_id():
    with pytest.raises(PersonaURIError):
        parse_uri("persona://")


def test_parse_uri_rejects_out_of_range_blend():
    with pytest.raises(PersonaURIError):
        parse_uri("persona://x?blend=1.5")


def test_validate_payload_warns_on_missing_consent_for_real_person():
    warnings = validate_payload(
        {
            "persona_id": "real-person-x",
            "consent": {"real_person": True},
            "blend": 0.0,
        }
    )
    assert any("missing-consent" in w for w in warnings)


def test_validate_payload_warns_on_deadbot_without_consent():
    warnings = validate_payload(
        {
            "persona_id": "deceased-y",
            "consent": {"deadbot": True},
            "blend": 0.0,
        }
    )
    assert any("missing-consent" in w for w in warnings)


def test_validate_payload_no_warning_with_consent_ref():
    warnings = validate_payload(
        {
            "persona_id": "real-person-z",
            "consent": {"real_person": True, "subject_consent_ref": "doc-id-123"},
            "blend": 0.0,
        }
    )
    assert warnings == []


def test_validate_payload_raises_without_persona_id():
    with pytest.raises(PersonaURIError):
        validate_payload({"consent": {}})
