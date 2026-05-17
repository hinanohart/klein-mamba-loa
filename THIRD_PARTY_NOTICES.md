# Third-Party Notices

This file lists upstream dependencies and the licenses under which they are
distributed. **This repository ships no model weights.** Downloading any
of the weights or assets referenced below subjects you to the corresponding
upstream license.

License classification ("GREEN / YELLOW / RED") is from our internal
audit on 2026-05-17. RED entries are listed for **awareness**, not as
runtime dependencies.

## GREEN — Apache 2.0 / MIT (commercial OSS distribution OK)

| Dependency | Purpose | License | Source |
|---|---|---|---|
| torch | tensor / autograd | BSD-3-Clause | pypi.org/project/torch |
| einops | tensor reshape DSL | MIT | pypi.org/project/einops |
| safetensors | weight serialization | Apache-2.0 | pypi.org/project/safetensors |
| huggingface-hub | weight download | Apache-2.0 | pypi.org/project/huggingface-hub |
| transformers | model loaders | Apache-2.0 | pypi.org/project/transformers |
| accelerate | dtype / device placement | Apache-2.0 | pypi.org/project/accelerate |
| diffusers | flux pipeline | Apache-2.0 | pypi.org/project/diffusers |
| mamba-ssm | Mamba-2 backbone | Apache-2.0 | github.com/state-spaces/mamba |
| causal-conv1d | mamba kernel | BSD-3-Clause | github.com/Dao-AILab/causal-conv1d |
| torchcfm | flow matching kernel | MIT | github.com/atong01/conditional-flow-matching |
| transfusion-pytorch | reference Transfusion impl | MIT | github.com/lucidrains/transfusion-pytorch |
| mem0ai | persona memory store | Apache-2.0 | pypi.org/project/mem0ai |
| lightrag-hku | graph RAG | Apache-2.0 | pypi.org/project/lightrag-hku |
| mcp | Model Context Protocol SDK | MIT | pypi.org/project/mcp |
| sglang | serving | Apache-2.0 | pypi.org/project/sglang |
| vllm | serving | Apache-2.0 | pypi.org/project/vllm |
| FLUX.2-klein-4b-fp8 (weights) | image generation | Apache-2.0 | huggingface.co/black-forest-labs/FLUX.2-klein-4b-fp8 |
| Lumina-Image-2.0 (weights, fallback) | image generation | Apache-2.0 | upstream |

## YELLOW — conditional (commercial OK with constraints)

The following are listed as optional plugins, **not** in default install:

| Dependency | License constraint |
|---|---|
| Janus-Pro 1.5B / 7B | MIT code + Attachment A use-restriction continuity; trademark restriction. Optional via `[flux]` extras subtree (planned). |
| SD 3.5 | Stability AI Community License; revenue ceiling, "Powered by Stability AI" attribution. **Not bundled.** |
| stable-audio-open | same as above. **Not bundled.** |
| NVIDIA Cosmos | commercial OK; safety guardrails MUST remain active; "Built on NVIDIA Cosmos" attribution required. **Not bundled.** |
| CogVideoX-5b | governed by PRC law; > 1M monthly visits requires additional license. **Not bundled.** |
| Llama 4 | 700M MAU cap; "Built with Llama" attribution; naming restriction. **Not bundled.** |
| FLUX.2-klein-9B | non-commercial; commercial use requires separate Self-Hosted Commercial agreement. **Not bundled; klein-4b only is GREEN.** |

## RED — non-commercial / forbidden in this OSS

These are **never** runtime dependencies:

- FLUX.1-dev / FLUX.1-Kontext-dev — FLUX.1 Non-Commercial License v1.1.1
- facebookresearch/flow_matching — CC BY-NC 4.0
- facebookresearch/memory (Memory Layers at Scale) — CC BY-NC 4.0
- chameleon-7b — Chameleon Research License (research only)
- EDM2 (NVlabs) — CC-BY-NC-SA 4.0
- HunyuanVideo — competing-service forbidden + EU/UK/Korea use forbidden
- Hunyuan3D-2 — > 1M MAU requires Tencent prior approval

If a future contribution introduces any of these as a runtime dependency,
it MUST be rejected by license-guard CI (`scripts/license_guard.py`,
implemented at S1 milestone).

## Datasets

- TIMETRAVEL (arXiv 1909.04076) — counterfactual narrative; used as
  evaluation seed only, no redistribution.

## How to update this file

When `pyproject.toml` changes:

```bash
python scripts/license_guard.py --refresh-notices  # planned, S1
```
