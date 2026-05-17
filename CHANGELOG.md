# Changelog

All notable changes are tracked here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased] — 0.0.1.dev0

### Added

- Initial S0 + S1 scaffold:
  - Apache-2.0 LICENSE, NOTICE, SECURITY.md, THIRD_PARTY_NOTICES.md
  - `pyproject.toml` with GREEN-only core dependencies and YELLOW
    items confined to optional extras
  - `klein_mamba_loa/persona/erasure.py`: default-on right-to-be-forgotten
    endpoint (LoRA + Mem0 namespace + LightRAG nodes)
  - `klein_mamba_loa/mcp/persona_scheme.py`: `persona://` URI parser
    and payload validator (0.1.0-draft)
  - `scripts/measure_vram.py`: S0-c VRAM measurement stub
- S2 SPF Loss core:
  - `klein_mamba_loa/flow/loss/pgc_dfm.py`: `PGCDisentangledFMLoss`,
    `SPFLossConfig`, `SPFLossOutput`, `orthogonality_penalty`
  - `klein_mamba_loa/persona/geometry.py`: orthogonal persona basis
    builder + SVD re-projection
  - `klein_mamba_loa/persona/disentangle.py`: angular orthogonality
    metric (S3 gate)
  - `klein_mamba_loa/backbone/mamba_transfusion_bridge.py`: surface
    for the Mamba ↔ Transfusion diffusion-head adapter
  - `klein_mamba_loa/eval/runtime_gate.py`: GREEN / YELLOW / RED
    classification helpers
  - 20 unit tests covering MCP scheme parsing, consent warnings,
    erasure, and the runtime gate
- S5 release-prep documentation:
  - `docs/MODEL_CARD.md`, `docs/ARCHITECTURE.md`, `docs/persona-rfc.md`,
    `CONTRIBUTING.md`, this `CHANGELOG.md`
  - GitHub Actions CI configuration

### Pending (gated)

- S3 integration toy (3-run loss-curve study) — requires a GPU host
- S4 small-scale eval against TIMETRAVEL branching ECE — depends on S3
- Real VRAM measurement — `scripts/measure_vram.py` exists; running
  it on a GPU host is a user action
- `gh repo search` against the four naming axes — pending `gh auth`
- Release tag — user-intervention point
