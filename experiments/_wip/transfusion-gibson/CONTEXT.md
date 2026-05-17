# CONTEXT — Transfusion-Gibson OSS (klein-mamba-loa)

最終更新: 2026-05-17 / 200 行以内 / /compact 跨ぎ recovery 用 entry point

## Freeze 参照

- 構想 freeze: `~/.claude/projects/-home-runza/memory/project_transfusion-gibson-oss-2026-05-17.md`
- 統合 blueprint: `~/.claude/projects/-home-runza/memory/architecture_transfusion-gibson-blueprint-2026-05-17.md`

新規 session で復元する場合、上記 2 file を最初に Read してから本 file を Read してください。

## 直近決定 log

### S0-a 命名 4 軸 verify — GREEN (2026-05-17)

- repo (GitHub) `klein-mamba-loa`: WebSearch 衝突なし
- PyPI package `klein-mamba-loa`: 衝突なし
- Python namespace `klein_mamba_loa`: 衝突なし
- arXiv title "Stratified Persona Flow: Disentangled Velocity Fields for Multi-Persona Multimodal Generation": 完全一致なし。`Persona-Flow` (arXiv 2602.15669) は OCEAN trait vector algebra 文脈で別物、SPF 命名で衝突回避
- Loss class `PGCDisentangledFMLoss`: 衝突なし
- 基盤論文 3 件実在確認: Geometry of Persona (2512.07092) / Disentangled FM (2602.05214) / Transfusion (2408.11039)

### S0-b Flux.2 klein 4B FP8 weight path — GREEN (2026-05-17)

- Repo: `black-forest-labs/FLUX.2-klein-4b-fp8` (HuggingFace)
- License: Apache 2.0 (商用 OSS 配布可)
- File: `flux-2-klein-base-4b-fp8.safetensors`, 4.09 GB
- VRAM: ~13 GB (RTX 3090 / 4070 以上)
- 代替 (RED 化に備え): Lumina-Image-2.0 (Apache 2.0)

### S0-c VRAM 実測 stub — IN_PROGRESS

- `scripts/measure_vram.py` 作成中
- 実 GPU 測定は user 側 (本 Claude 環境に GPU 想定なし、stub の構造のみ verify)

## 確定 Tier1 stack (24GB 1 GPU)

| 役 | model | 入手 | VRAM | License |
|---|---|---|---|---|
| 画像生成 | FLUX.2 klein 4B (FP8) | HF black-forest-labs/FLUX.2-klein-4b-fp8 | ~8 GB | Apache 2.0 |
| text backbone | Mamba-2 1.3B (BF16) | state-spaces/mamba | ~3 GB | Apache 2.0 |
| memory | Mem0 + LightRAG | PyPI | 0 (外部 DB) | Apache/MIT |
| persona | LoRA adapter | 自作 | ~0.3 GB | Apache 2.0 (本 OSS) |
| tool | MCP layer | mcp PyPI | CPU 側 | MIT |
| serving | sglang / vllm | PyPI | — | Apache 2.0 |

合計 weight ~11-14 GB + KV ~2-4 GB + activation ~3 GB = **18-21 GB / 24 GB**

排他 load 制約: Mamba-2 と Janus-Pro 1.5B (~6GB YELLOW) は同時 load 不可 (Tier1)。

## 確定 革新 primitive

**Stratified Persona Flow (SPF) Loss** (内部 class 名 `PGCDisentangledFMLoss`):

```
L = E_t[||v_pred - v_target||^2]
  + lambda_ortho * sum_{i != j} | <P_i, P_j> |^2
  + lambda_cond * CE(persona_id | v_pred)
```

- 学習対象 = persona basis + cond_proj + LoRA のみ、backbone freeze
- hypothesis 段階扱い、実証前 claim 禁止
- bootstrap CI で λ tuning 必須 (3 run 平均、S3 gate)

## Pipeline 進行

```
S0 (verify) -> S1 (scaffold) -> S2 (SPF Loss core) -> S3 (toy 3-run) -> S4 (eval) -> S5 (docs + release prep)
合計 9-12 session 目安、Tier1 toy demo (loss 下降確認) は S0-S3 = 5-6 session
```

## Gate condition

- GREEN: test + lint + license + kluster all pass → 次 stage 自動進行
- YELLOW: 一部 fail / VRAM +10% 超過 / kluster medium → 1 retry、再 fail で stop
- RED: license RED / secret leak / network egress 必要 / ethical flag / >500 行 root 変更 / kluster critical → 即停止 + user 報告

## User 介入必須 trigger (R7 自走対象外)

Network egress / License RED / Release tag (`v*`) / arXiv 投稿 / 実在人物 dataset / Secret config (R11) / sub-R14 結論採否 / Tier 再定義

## 監視 agent 体制 (本 session で並行起動中)

- monitor1: blueprint § 10 step 1-7 contract 実行漏れ verify
- monitor2: freeze + blueprint key facts 把握 verify
- meta: monitor1 / monitor2 の blind spot + R11/R13/kluster compliance 独自 check

## 禁則 (永続)

- 「完全自動」「永続的」訴求 ← `feedback_no-permanent-claim-2026-05-14`
- commit message に R 番号 ← `feedback_no-r-numbers-in-commits-2026-05-15`
- `rm -rf` ← R8、失敗は `experiments/_wip/<name>/failures/<stage>-<ts>/`
- secret 直扱い ← R11 (HF token は env var 経由のみ)
- 実在人物 personality cloning ← 同意なし不可
- deadbot ← 法整備未成熟、policy 層のみ

## 進捗 (2026-05-17 本 session 完了時点)

### Claude-driven GREEN (43 tracked file, 3 commits)

- **S0**: 命名 4 軸 verify GREEN / Flux.2 klein 4B FP8 weight path GREEN / VRAM stub structural GREEN
- **S1**: LICENSE / NOTICE / SECURITY / THIRD_PARTY_NOTICES (GREEN/YELLOW/RED audit) / pyproject.toml / .gitignore / README
- **S2 core**: PGCDisentangledFMLoss (233 行 / 500 行 sub-R14 cap 内) / orthogonality_penalty / make_persona_basis / RuntimeGate / mamba_transfusion_bridge stub / 20 unit tests passing on no-torch path
- **S5 CPU portion**: MODEL_CARD / ARCHITECTURE / persona-rfc (MCP 0.1.0-draft) / CONTRIBUTING / CHANGELOG / .pre-commit-config / .github/workflows/ci.yml / scripts/license_guard.py (23 deps scanned, 0 RED)

git 履歴: `981af1a` initial → `0a26f1f` S2 core → `01e4914` S5 docs

### User-gated (GPU host or external action 必要)

- **S3 toy 3-run training**: GPU host で Mamba-2 1.3B + Flux.2 klein 4B FP8 load + SPF Loss 1k step、loss curve 3 run 平均下降、orthogonality >= 0.7
- **S4 small-scale eval**: TIMETRAVEL branching ECE baseline 比較
- **S3 着手 file**: `examples/toy_train.py` (本 session 未作成、user-driven session で書く想定)
- **真の VRAM 測定**: `python scripts/measure_vram.py --tier 1` を GPU host で
- **gh repo create / push**: HF token / GH token は R11 で env var 経由のみ
- **release tag / arXiv 投稿**: blueprint § 7 user-intervention point

## 関連 memory link

- [[project_transfusion-gibson-oss-2026-05-17]]
- [[architecture_transfusion-gibson-blueprint-2026-05-17]]
- [[critical-rules-core]] R7 / R11 / R13 / R14 / R16 / R17
- [[feedback_no-permanent-claim-2026-05-14]]
- [[feedback_no-r-numbers-in-commits-2026-05-15]]
