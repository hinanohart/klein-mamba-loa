"""Janus-Pro 1.5B wrapper (Tier1 exclusive-load alternative to Mamba-2).

Janus-Pro and Mamba-2 cannot co-reside on a 24GB GPU at training-time
(blueprint section 3 — Tier1 exclusive-load constraint). This wrapper is
the swap-in alternative; S2 will surface the load order guard.

License: DeepSeek (YELLOW) — Attachment A use-restrictions inherit. The
THIRD_PARTY_NOTICES.md YELLOW row covers the audit.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JanusProConfig:
    repo_id: str = "deepseek-ai/Janus-Pro-1.5B"
    dtype: str = "bfloat16"


class JanusProBackbone:
    def __init__(self, config: JanusProConfig | None = None):
        self.config = config or JanusProConfig()
        self._model = None

    def load(self):
        raise NotImplementedError(
            "JanusProBackbone.load is S2 work; surface only at S1. "
            "Note: cannot co-load with Mamba-2 on Tier1 (24GB)."
        )

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("JanusProBackbone forward is S2 work.")
