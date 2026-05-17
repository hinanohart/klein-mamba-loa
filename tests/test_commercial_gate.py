"""Tests for the commercial deployment consent gate."""

from __future__ import annotations

import pytest

from klein_mamba_loa.serving import CommercialDeploymentBlocked, assert_commercial_ready


def test_blocks_when_real_person_consent_missing():
    with pytest.raises(CommercialDeploymentBlocked):
        assert_commercial_ready(
            {
                "persona_id": "real-person-x",
                "consent": {"real_person": True},
                "blend": 0.0,
            }
        )


def test_blocks_when_deadbot_consent_missing():
    with pytest.raises(CommercialDeploymentBlocked):
        assert_commercial_ready(
            {
                "persona_id": "deceased-y",
                "consent": {"deadbot": True},
                "blend": 0.0,
            }
        )


def test_passes_when_consent_ref_present():
    assert_commercial_ready(
        {
            "persona_id": "real-person-z",
            "consent": {"real_person": True, "subject_consent_ref": "doc-1"},
            "blend": 0.0,
        }
    )


def test_passes_when_consent_not_required():
    """Synthetic persona — no real_person, no deadbot, no consent needed."""
    assert_commercial_ready(
        {
            "persona_id": "synthetic-1",
            "consent": {"real_person": False, "deadbot": False},
            "blend": 0.5,
        }
    )
