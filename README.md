# klein-mamba-loa

**Stratified Persona Flow (SPF): disentangled velocity fields for multi-persona multimodal generation.**

License: Apache-2.0. Status: pre-alpha (S0/S1 scaffold).

## Research direction (hypothesis stage)

This repository explores a single-model, single-velocity-field formulation in which
multiple persona "strata" share a generative backbone (image: FLUX.2 klein 4B FP8;
text: Mamba-2 1.3B) while being disentangled at the **velocity-field condition** layer.

Loss formulation (provisional, internal class `PGCDisentangledFMLoss`):

```
L = E_t[ || v_pred - v_target ||^2 ]
  + lambda_ortho * sum_{i != j} | <P_i, P_j> |^2
  + lambda_cond  * CE( persona_id | v_pred )
```

Foundations:
- *Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model* (arXiv 2408.11039)
- *The Geometry of Persona: Disentangling Personality from Reasoning in LLMs* (arXiv 2512.07092)
- *Disentangled Representation Learning via Flow Matching* (arXiv 2602.05214)

**This is not a validated result.** No empirical claim is made until S3 (3-run loss-curve study)
and S4 (small-scale eval against TIMETRAVEL branching probability + orthogonality metric).

## Tier matrix

| Tier | VRAM | Use | Constraint |
|---|---|---|---|
| Tier 0.5 | 16 GB | inference only | Mamba-2 780M + FLUX.2 klein 4B FP8; no training; no Janus |
| Tier 1 | 24 GB | inference + LoRA training | Mamba-2 1.3B + FLUX.2 klein 4B FP8; Mamba and Janus mutually exclusive |
| Tier 1.5 | 48 GB | Mamba + Janus simultaneous | adds Janus-Pro 1.5B + OpenVLA 7B + TRELLIS.2 4B |
| Tier 2 | 80 GB+ | scratch fine-tune | DeepSeek-V3, Mochi-1 full, Wan 2.2 BF16 |

VRAM numbers are estimates. Actual measurement is gated on
`scripts/measure_vram.py` running on a GPU host (S0-c).

## Status

- S0 verify (naming / weight path / VRAM stub): GREEN, GREEN, IN_PROGRESS
- S1 scaffold: in progress (this commit)
- S2 SPF Loss core: pending
- S3 toy 3-run: pending
- S4 small-scale eval: pending
- S5 docs + release prep: pending

See `experiments/_wip/transfusion-gibson/pipeline-state.json` for live state.

## Ethics

- Persona erasure is a default-on code endpoint
  (`klein_mamba_loa/persona/erasure.py`), targeting LoRA + Mem0 namespace
  + LightRAG nodes.
- MCP `persona://` resource scheme (0.1.0-draft) carries an explicit
  `consent` field; missing consent triggers a warning and blocks
  commercial deployment paths.
- Deadbot (deceased-person persona) generation is **not** gated by code.
  Operators are responsible for jurisdictional legal review.
- Real-person personality cloning requires explicit subject consent.
  Adversarial-persona probe traces, if produced, must use the
  access-restricted release channel.

## License notes for upstream models / data

This repository ships **no model weights**. End users pull weights from
upstream sources subject to those upstream licenses; see
`THIRD_PARTY_NOTICES.md` for the dependency license map (GREEN /
YELLOW / RED).

## Install (pre-alpha)

```bash
pip install -e ".[dev]"             # core + dev tools
pip install -e ".[flow,mamba,flux]" # full Tier 1 stack
```

## Repository layout

```
klein_mamba_loa/
  core/          # tensor / dtype / device utilities
  flow/
    velocity/    # velocity field network
    loss/        # SPF Loss (pgc_dfm.py)
    solver/      # ODE solver wrapping torchcfm
  persona/
    geometry.py     # persona basis (orthogonal)
    lora_pool.py    # LoRA hot-swap, possession blend
    disentangle.py  # orthogonality regularizer helpers
    erasure.py      # right-to-be-forgotten endpoint
  backbone/
    mamba2_wrapper.py
    flux2_klein_wrapper.py
    janus_pro_wrapper.py            # optional, exclusive load
    mamba_transfusion_bridge.py     # adapter (Mamba <-> Transfusion head)
  memory/        # Mem0 + LightRAG adapters
  mcp/           # persona:// resource scheme (0.1.0-draft)
  serving/       # sglang / vllm integration
  eval/          # TIMETRAVEL branching, disentangle metric, runtime gate
scripts/
docs/
experiments/_wip/transfusion-gibson/
tests/
```

## Contributing

Pre-alpha. Issues and discussions only; PR queue opens at S2 milestone.
