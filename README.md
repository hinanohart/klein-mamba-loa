# klein-mamba-loa

**Stratified Persona Flow (SPF): disentangled velocity fields for multi-persona multimodal generation.**

License: Apache-2.0. Status: pre-alpha (S0/S1 scaffold + S2 SPF Loss core + S5 release-prep docs; S3/S4 user-gated on GPU).

## Research direction (hypothesis stage)

This repository explores a single-model, single-velocity-field formulation in which
multiple persona "strata" share a generative backbone (image: FLUX.2 klein 4B FP8;
text: Mamba-2 1.3B) while being disentangled at the **velocity-field condition** layer.

Loss formulation (provisional, internal class `PGCDisentangledFMLoss`):

```
L = E_t[ || v_pred - v_target ||^2 ]
  + lambda_ortho * sum_{i < j} | <P_i, P_j> |^2
  + lambda_cond  * CE( persona_id | <pooled v_pred, P> )
```

Foundations (see `docs/REFERENCES.md` for retrieved-at evidence — these arXiv IDs are `pending-human-verify` and MUST be opened in a browser before citing in any external publication; `USER_ACTIONS.sh references-verify` is the flip):

- *Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model* (arXiv 2408.11039) [unverified]
- *The Geometry of Persona: Disentangling Personality from Reasoning in LLMs* (arXiv 2512.07092) [unverified]
- *Disentangled Representation Learning via Flow Matching* (arXiv 2602.05214) [unverified]

**This is not a validated result.** No empirical claim is made until S3 (3-run loss-curve study)
and S4 (small-scale eval against TIMETRAVEL branching probability + orthogonality metric).

## Tier matrix

| Tier | VRAM | Use | Constraint |
|---|---|---|---|
| Tier 0.5 | 16 GB | inference only | Mamba-2 780M + FLUX.2 klein 4B FP8; no training; no Janus |
| Tier 1 | 24 GB | inference + LoRA training | Mamba-2 1.3B + FLUX.2 klein 4B FP8; Mamba and Janus mutually exclusive |
| Tier 1.5 | 48 GB | Mamba + Janus simultaneous | adds Janus-Pro 1.5B + OpenVLA 7B + TRELLIS.2 4B |
| Tier 2 | 80 GB+ | scratch fine-tune | DeepSeek-V3, Mochi-1 full, Wan 2.2 BF16 |

VRAM numbers are estimates. Real measurement requires a GPU host —
run `python scripts/measure_vram.py --tier 1`. On a CPU host the stub
returns `gate=DRY_RUN` (structural verification only).

## Status

| Stage | Status | Notes |
|---|---|---|
| S0-a (naming 4-axis) | GREEN | WebSearch verified |
| S0-b (FLUX.2 klein 4B FP8 weight path) | GREEN | Apache-2.0 confirmed |
| S0-c (VRAM measurement) | DEFERRED to GPU host | dry-run returns `DRY_RUN`; real measurement is a user gate |
| S1 (scaffold + license guard) | GREEN | `THIRD_PARTY_NOTICES.md` + `scripts/license_guard.py` |
| S2 (SPF Loss core) | GREEN (CPU) | `klein_mamba_loa/flow/loss/pgc_dfm.py`, unit tests pass on no-torch host |
| S3 (toy 3-run training) | USER GATE (GPU) | `examples/toy_train.py` scaffold ready; needs GPU host |
| S4 (small-scale eval) | USER GATE (GPU) | depends on S3 |
| S5 (docs + release prep) | GREEN (CPU portion) | release tag is user-intervention point |

Live state: `experiments/_wip/transfusion-gibson/pipeline-state.json`.

## Concept naming disclaimer

The repository name (`loa`) and several internal labels — "Persona-
Geometry", "Stratified Persona Flow", "Loa hot-swap" — are
**inspirational labels for technical primitives**, not claims of
literary equivalence to William Gibson's Sprawl trilogy or to any
other prior persona-vector formalism. The concept-to-technology
mapping is many-to-many and wishful only at the framing level. In
particular:

- a `PersonaVector` here is a learned condition direction, **not**
  Dixie Flatline (no persistent memory, no self-identity).
- LoRA hot-swap is **not** Loa possession in the literary sense
  (no agency transfer between substrates).
- "Stratified Persona Flow" deliberately differs from the prior
  arXiv 2602.15669 "Persona-Flow" (OCEAN trait vector algebra) —
  same word, different formalism (see `docs/REFERENCES.md`).

## Ethics

- **Right to be forgotten** is implemented as a default-on code endpoint
  (`klein_mamba_loa/persona/erasure.py`). **Scope at S1**: the LoRA-pool
  directory `weights/lora_pool/<id>/` is recursively removed. **Not yet
  at S1**: Mem0 namespace cleanup and LightRAG node filter cleanup —
  the adapters land at S2. Operators relying on the endpoint today must
  also delete from Mem0/LightRAG manually; `ErasurePlan.warnings`
  surfaces this gap explicitly.
- The MCP `persona://` resource scheme (0.1.0-draft) carries an explicit
  `consent` field. Missing `subject_consent_ref` for `real_person=true`
  or `deadbot=true` produces a `missing-consent` warning from
  `validate_payload`, which `serving/commercial_gate.py` turns into a
  hard `CommercialDeploymentBlocked` exception on the commercial path.
- **Deadbot (deceased-person persona) generation is not gated by code.**
  Operators are responsible for jurisdictional legal review.
- **Real-person personality cloning** requires explicit subject consent.
  Adversarial-persona probe traces, if produced, must use the
  access-restricted release channel.

## License notes for upstream models / data

This repository ships **no model weights**. End users pull weights from
upstream sources subject to those upstream licenses; see
`THIRD_PARTY_NOTICES.md` for the dependency license map (GREEN /
YELLOW / RED).

## Install (pre-alpha)

```bash
pip install -e ".[dev,mcp]"             # CPU-only core + tests
pip install -e ".[flow,mamba,flux]"     # full Tier 1 stack (needs GPU host for runtime)
```

`torch` lives in the `[flow]` / `[mamba]` / `[flux]` extras to keep
CPU-only S0 verification light (no 800 MB torch download in core CI).

## Repository layout

```
klein_mamba_loa/
  core/           # placeholder — tensor / dtype utilities (S2+)
  flow/
    velocity/     # placeholder (S3)
    loss/         # SPF Loss (pgc_dfm.py)
    solver/       # placeholder (S3)
  persona/
    geometry.py     # persona basis (orthogonal)
    lora_pool.py    # LoRA hot-swap surface (NotImplementedError until S2)
    disentangle.py  # orthogonality metric (angular_orthogonality)
    erasure.py      # right-to-be-forgotten endpoint (LoRA-only at S1)
  backbone/
    mamba2_wrapper.py             # surface (concrete load = S2)
    flux2_klein_wrapper.py        # surface (concrete load = S2)
    janus_pro_wrapper.py          # surface (concrete load = S2)
    mamba_transfusion_bridge.py   # adapter surface (forward = S2)
  memory/         # placeholder (S2 Mem0 + LightRAG adapters)
  mcp/            # persona:// resource scheme (0.1.0-draft)
  serving/
    commercial_gate.py            # missing-consent BLOCK (S1)
  eval/
    runtime_gate.py # GREEN/YELLOW/RED classifier (S0-c, S3)
scripts/
  measure_vram.py        # S0-c VRAM stub
  license_guard.py       # RED-license refusal
  check_file_lengths.py  # sub-R14 500-line cap automation
docs/
  ARCHITECTURE.md
  MODEL_CARD.md
  REFERENCES.md          # arXiv evidence
  persona-rfc.md         # MCP persona:// RFC 0.1.0-draft
experiments/_wip/transfusion-gibson/
  pipeline-state.json    # current stage, gates, kluster chat_id, git_sha
  CONTEXT.md             # narrative log
  TODO_NEXT.md           # top-3 next actions
  monitor_logs/          # audit-agent outputs (append-only)
  failures/              # R8 permanent failure parking
examples/
  toy_train.py           # S3 training harness scaffold (CPU-importable, GPU runnable)
tests/
USER_ACTIONS.sh          # one-script bundle of every remaining manual step
```

## Contributing

Pre-alpha. Issues and discussions only; PR queue opens at S2 milestone.
Read `CONTRIBUTING.md` for the anti-checklist (no RED-license deps, no
empirical claim before S3, no erasure removal).
