# Model Card — klein-mamba-loa / Stratified Persona Flow (SPF)

**Status**: pre-alpha. **No trained checkpoint** is released by this
repository. This card documents the intended training/eval recipe and
the responsible-use envelope.

## Overview

`klein-mamba-loa` proposes **Stratified Persona Flow (SPF)**: a
single-velocity-field formulation in which multiple persona strata
share a generative backbone (text: Mamba-2 1.3B; image: FLUX.2 klein
4B FP8) while remaining disentangled at the velocity-field
condition layer.

Internal training symbol: `PGCDisentangledFMLoss`
(Persona-Geometry-Conditioned Disentangled Flow Matching).

## Intended use

- research on persona-conditional multimodal generation
- evaluation of disentanglement metrics on TIMETRAVEL-style
  counterfactual branching data
- proof-of-concept for the MCP `persona://` resource scheme

## Out-of-scope use

- **production deployment of real-person personas without explicit
  consent** is out of scope. See `SECURITY.md`.
- **deadbot (deceased-person persona)** generation is **not**
  technically blocked. Operators are responsible for jurisdictional
  legal review prior to any such deployment.
- **adversarial persona probing** results, if produced, must be
  released through the access-restricted release channel only.

## Training data (planned)

- **TIMETRAVEL** (arXiv 1909.04076) — counterfactual narrative
  branching, evaluation seed only.
- Public-domain text + Creative Commons multimodal pairs (corpus
  list to be finalized at S3).

**No real-person personality corpora** are included.

## Architecture

| Component | Model | Size | License | Source |
|---|---|---|---|---|
| Text backbone | Mamba-2 | 1.3B (BF16) | Apache-2.0 | state-spaces/mamba |
| Image backbone | FLUX.2 klein | 4B (FP8) | Apache-2.0 | black-forest-labs/FLUX.2-klein-4b-fp8 |
| Velocity head | bespoke | depends on backbone | Apache-2.0 (this repo) | this repo |
| Persona basis | learned | (num_personas, dim) | Apache-2.0 (this repo) | this repo |
| Memory store | Mem0 + LightRAG | external | Apache-2.0 | upstream |

## Loss

```
L_total = E_t[ || v_pred - v_target ||^2 ]                  (FM term)
        + lambda_ortho * sum_{i != j} | <P_i, P_j> |^2       (persona orthogonality)
        + lambda_cond  * CE( persona_id | v_pred )           (conditional id recovery)
```

`lambda_ortho` and `lambda_cond` are determined empirically by the S3
3-run loss-curve study. No claim of optimality is made at this stage.

## Eval (planned at S4)

- branching-probability ECE on TIMETRAVEL counterfactual subset
  (1e4 pairs) against an unconditioned baseline
- angular orthogonality of the persona basis (>= 0.7 threshold)
- ablation: lambda_ortho in {0, 1e-3, 1e-2, 1e-1}, lambda_cond in
  {0, 1e-2, 1e-1, 1.0}

## Hardware (S0-c structural verify; real measurement is user-host)

| Tier | VRAM | Use |
|---|---|---|
| Tier 0.5 | 16 GB | inference only |
| Tier 1 | 24 GB | inference + LoRA training |
| Tier 1.5 | 48 GB | Mamba + Janus simultaneously |
| Tier 2 | 80 GB+ | scratch fine-tune |

## Limitations

- Stage 0 verifications are structural; the loss formulation is
  hypothesis stage.
- LoRA hot-swap and Mamba-Transfusion bridge are surface-only stubs
  at this commit.
- The orthogonality regularizer is a learning-time bias, **not** a
  cryptographic guarantee of information isolation between persona
  strata.

## License

Code under Apache-2.0. Upstream model weight licenses apply when
downloading; see `THIRD_PARTY_NOTICES.md`.

## Citation

Until preprint v1 is published, cite this repository:

```
@software{klein_mamba_loa_2026,
  title  = {klein-mamba-loa: Stratified Persona Flow for multi-persona
            multimodal generation},
  year   = {2026},
  url    = {https://github.com/REPLACE_ME/klein-mamba-loa},
  note   = {pre-alpha, hypothesis stage}
}
```
