# Architecture

This document is the operational counterpart of the research blueprint.
For the upstream design discussion, see the project's internal blueprint
note (not in this repository).

## High-level diagram

```
                  +-----------------------+
                  |   MCP persona:// URI  |
                  |   (consent, blend)    |
                  +-----------+-----------+
                              |
                              v
                  +-----------+-----------+
                  | persona/geometry.py   |   (orthogonal basis P_1..P_n)
                  | persona/lora_pool.py  |   (hot-swap / blend)
                  +-----------+-----------+
                              |
   +---------------+          v          +---------------+
   |  Mamba-2 1.3B +--+-->[ bridge ]-->--+ FLUX.2 klein  |
   |  (text)       |  |                  | 4B FP8 (img)  |
   +---------------+  |                  +-------+-------+
                      v                          |
              +-------+-------+                  v
              |   velocity    |          +-------+-------+
              |    field      |          |  diffusion    |
              +-------+-------+          |  head         |
                      |                  +-------+-------+
                      |                          |
                      +-------------+------------+
                                    v
                          +---------+---------+
                          | SPF Loss (PGC-DFM)|
                          |  L_fm + L_ortho   |
                          |     + L_cond      |
                          +-------------------+
```

## Module boundaries

`klein_mamba_loa/` is a single namespace; sub-packages map 1:1 to the
diagram nodes above.

- `core/` — tensor / dtype / device utilities; deliberately small.
- `flow/` — velocity field, SPF Loss (`flow/loss/pgc_dfm.py`), ODE
  solver wrapper.
- `persona/` — geometry (orthogonal basis), LoRA pool (hot-swap),
  disentangle metrics, code-layer **erasure**.
- `backbone/` — Mamba-2, FLUX.2 klein, optional Janus-Pro, and the
  Mamba-Transfusion bridge that adapts Mamba hidden states into the
  Transfusion diffusion head.
- `memory/` — Mem0 and LightRAG adapters.
- `mcp/` — `persona://` resource scheme (0.1.0-draft) parser and
  payload validator.
- `eval/` — TIMETRAVEL branching ECE, disentangle metrics, runtime
  gate (GREEN / YELLOW / RED classification).
- `serving/` — sglang / vllm wrappers (S5 release).
- `scripts/` — operational helpers (`measure_vram.py`, future
  `license_guard.py`).

## Pipeline stages

| Stage | Output | Gate |
|---|---|---|
| S0 | naming verified / weight path / VRAM stub | GREEN if 3 sub-tasks all GREEN |
| S1 | scaffold, license guard | RED-license count = 0 |
| S2 | SPF Loss core, persona basis, bridge stubs, tests | gradient finite + tests pass |
| S3 | integration toy 3 runs | mean loss curve decreasing; orthogonality >= 0.7 |
| S4 | small-scale eval | ECE < baseline; orthogonality persists |
| S5 | docs + release prep | all docs filled; CI green; release tag (user gate) |

The sub-R14 trigger is `>500 lines OR module-crossing structural
change`. Stage S3 evaluation requires 3 independent runs before YELLOW
or RED is declared, to avoid acting on a single noisy curve.

## User-intervention points

The following actions are **never** taken automatically:

- network egress for non-public assets
- introducing any RED-license dependency
- release tagging (`v*`)
- arXiv submission
- ingestion of any real-person dataset
- secret / token configuration
- Tier definition changes
- accepting or rejecting a sub-R14 finding

Each occurrence stops the pipeline and surfaces a report.

## Ethics gate layers

| Concern | Layer | Location |
|---|---|---|
| Consent | protocol | `mcp/persona_scheme.py` (`consent.subject_consent_ref`) |
| Right to be forgotten | code | `persona/erasure.py` (default on) |
| Deadbot disclaimer | policy | `README.md` / `SECURITY.md` / `docs/MODEL_CARD.md` |

The code-layer erasure is the only one with hard enforcement; the
others are an obligation of operators and reviewers.

## Repository state files

Live state lives in `experiments/_wip/transfusion-gibson/`:

- `pipeline-state.json` — single source of truth for stage status
- `CONTEXT.md` — narrative log (<= 200 lines), survives `/compact`
- `TODO_NEXT.md` — top-3 next actions

A future `/compact` boundary recovers context by reading the three
files in that order plus the upstream blueprint note.
