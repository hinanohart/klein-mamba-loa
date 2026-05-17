# CONTEXT — Transfusion-Gibson OSS (klein-mamba-loa)

最終更新: 2026-05-18 (residual audit 完了時点) / 200 行以内 / /compact 跨ぎ recovery 用 entry point

## Freeze 参照

- 構想 freeze: `~/.claude/projects/-home-runza/memory/project_transfusion-gibson-oss-2026-05-17.md`
- 統合 blueprint: `~/.claude/projects/-home-runza/memory/architecture_transfusion-gibson-blueprint-2026-05-17.md`

新規 session で復元する場合、上記 2 file を最初に Read してから本 file を Read してください。

## 直近決定 log

### 2026-05-18 residual audit pass

primary audit (2026-05-17) を疑って 3 並列再探索: architect / verifier / critic。critic verdict は **REJECT** (5/5 pre-commitment hit)。**全件 self-fix 完了**:

- `scripts/license_guard.py`: 真の parser 実装。前の regex は `**name**` bold 要求で実 file (plain text bullets) から 0 抽出していた。bold/plain 両形式、em-dash/en-dash/--、slash-alternation、paren alias を扱う。PEP 503 canonical 比較で `flow_matching` ↔ `flow-matching` 同一視。
- `.github/workflows/ci.yml`: `torch-tests` job 追加。CPU torch wheel + test_pgc_dfm/geometry/disentangle が CI 上で走る。
- `docs/persona-rfc.md`: `persona_id` 正規表現を impl と統一、`rev` semantics を weights-bundle sha と明記、query-key uniqueness / path-after-authority も文書化。
- `examples/toy_train.py` + `docs/MODEL_CARD.md`: synthetic target が basis 自身由来で "convergence" が機械的であることを明示 — 構造検証であって科学的検証ではない。
- `USER_ACTIONS.sh`: placeholder-org rewrite を pyproject 以外 (MODEL_CARD, README, REFERENCES) にも拡張。
- `README.md`: 三本 arXiv ID に inline `[unverified]` marker。Gibson disclaimer paragraph 追加 (Persona Vector ≠ Dixie Flatline)。
- `docs/MODEL_CARD.md`: limitations に toy_train degeneracy + Gibson disclaimer。
- `klein_mamba_loa/{core,flow/velocity,flow/solver,memory}/__init__.py`: S1 status disclosure に書き換え (前は "S2 wiring" 一行で empty 状態を隠蔽していた)。
- `tests/`: test_backbone_surface, test_lora_pool, test_measure_vram, test_toy_train_import 追加 + test_commercial_gate に malformed payload テスト追加。
- `tests/test_license_guard.py`: parser を実 file で exercise する regression test。
- `THIRD_PARTY_NOTICES.md` / `CONTRIBUTING.md` / `docs/ARCHITECTURE.md`: "planned" 用語を実装済に更新、CONTRIBUTING anti-checklist に check_file_lengths / commercial_gate / REFERENCES verify を追加。
- `.gitignore`: vram_report.json / toy_train_report.json を ignore、tracked vram_report.json を untrack。
- `experiments/_wip/transfusion-gibson/monitor_logs/2026-05-18-*.md`: 3 agent の生 verdict を persist (false-positive 教訓を operationalize)。

検証: 85/85 pytest pass、license_guard 真 parser 経由で 25 deps 0 RED、check_file_lengths OK。

### 2026-05-17 audit pass (前 session)

3 並列 read-only agent (architect / omc-code-reviewer / critic) で CRITICAL × 5、MAJOR × 11、MINOR 多数、OPEN blueprint remainder 6 を発見。**全件 self-fix 完了**:

- `pgc_dfm.py`: `detach_basis_for_cond` 実装、basis-projection 内蔵 cond head、`Σ_{i<j}` 化
- `mcp/persona_scheme.py`: rev hex8 validation、persona_id 正規表現、path-after-authority 拒否
- `persona/erasure.py`: rglob + shutil.rmtree、Mem0/LightRAG S2-pending を `warnings` で明示
- `backbone/`: mamba2 / flux2_klein / janus_pro wrapper surface 追加 (measure_vram の import 復活)
- `serving/commercial_gate.py`: `assert_commercial_ready` で missing-consent BLOCK 実コード化
- `eval/runtime_gate.py`: config validation 追加
- `persona/disentangle.py`: 強い上三角 sum で 0-norm row 耐性
- `scripts/license_guard.py`: THIRD_PARTY_NOTICES.md 解析 + UTF-8 明示 + _pkg_name min-index 修正
- `scripts/check_file_lengths.py`: 500-LOC sub-R14 trigger 自動化、pre-commit + CI 配線
- `pyproject.toml`: torch を [flow]/[mamba]/[flux] へ、`[all]` に `[serving]` 追加、authors 設定
- `.github/workflows/ci.yml`: torch なし CI、mypy lenient step 追加
- `docs/REFERENCES.md`: arXiv 3 本の retrieved-at evidence (pending-human-verify)
- `docs/MODEL_CARD.md`, `README.md`, `SECURITY.md`: erasure scope 訂正、consent BLOCK 実コード参照、S0-c status 統一
- `examples/toy_train.py`: S3 toy training scaffold (CPU-importable)
- `experiments/_wip/transfusion-gibson/{monitor_logs,failures}/`: audit ログと R8 failure parking
- `USER_ACTIONS.sh`: 残る人間 step 8 件を一本化

### 検証
- 65/65 pytest pass (no-torch path 48 + torch path 17)
- license_guard 25 deps 0 RED
- check_file_lengths 500-LOC cap OK
- measure_vram --dry-run gate=DRY_RUN
- toy_train.py --steps 20 mean_final_ortho ≈ 1.0、all_runs_decreased=true

### 2026-05-17 audit pass 前 (前 session)

- S0-a 命名 4 軸 verify GREEN / S0-b Flux.2 klein 4B FP8 GREEN / S0-c VRAM stub GREEN_STRUCTURAL → DEFERRED_TO_GPU_HOST へ語彙統一
- S1 scaffold、S2 SPF Loss core、S5 release-prep docs を commit

## 確定 Tier1 stack (24GB 1 GPU)

| 役 | model | 入手 | VRAM | License |
|---|---|---|---|---|
| 画像生成 | FLUX.2 klein 4B (FP8) | HF black-forest-labs/FLUX.2-klein-4b-fp8 | ~8 GB | Apache 2.0 |
| text backbone | Mamba-2 1.3B (BF16) | state-spaces/mamba | ~3 GB | Apache 2.0 |
| memory | Mem0 + LightRAG | PyPI | 0 (外部 DB) | Apache/MIT |
| persona | LoRA adapter | 自作 | ~0.3 GB | Apache 2.0 (本 OSS) |
| tool | MCP layer | mcp PyPI | CPU 側 | MIT |
| serving | sglang / vllm | PyPI | — | Apache 2.0 |

合計 weight ~11-14 GB + KV ~2-4 GB + activation ~3 GB = **18-21 GB / 24 GB**。Mamba-2 と Janus-Pro 1.5B は同時 load 不可。

## 確定 革新 primitive

**Stratified Persona Flow (SPF) Loss** (内部 class 名 `PGCDisentangledFMLoss`):

```
L = E_t[||v_pred - v_target||²]
  + lambda_ortho * Σ_{i<j} | <P_i, P_j> |²
  + lambda_cond * CE(persona_id | <pooled v_pred, P>)
```

学習対象 = persona basis + 内蔵 cond projection、backbone freeze。hypothesis 段階。

## Pipeline 進行

```
S0 (verify) -> S1 (scaffold) -> S2 (SPF Loss core) -> S3 (toy 3-run) -> S4 (eval) -> S5 (docs + release prep)
S0/S1/S2 core/S5 CPU portion = GREEN (Claude 自走完了)
S3/S4 = USER_GATE_GPU_REQUIRED (USER_ACTIONS.sh で集約)
```

## User 介入必須 (R7 自走対象外)

すべて `USER_ACTIONS.sh --plan` に集約 (8 step):

1. github-repo-create — gh auth login が前提
2. hf-login — HF_TOKEN env var or 対話
3. install-tier1 — GPU host で torch + deps
4. measure-vram — GPU host で real S0-c
5. toy-train-3run — S3 gate
6. references-verify — 人間が arXiv 3 本の abstract sha を埋める
7. release-tag — REFERENCES が verified でないと拒否
8. arxiv-submit — browser で arxiv.org/submit を開く

## 禁則 (永続)

- 「完全自動」「永続的」訴求 ← `feedback_no-permanent-claim-2026-05-14`
- commit message に R 番号 ← `feedback_no-r-numbers-in-commits-2026-05-15`
- `rm -rf` ← R8、失敗は `experiments/_wip/<name>/failures/<stage>-<ts>/`
- secret 直扱い ← R11 (HF token / GH token は env var 経由のみ、`USER_ACTIONS.sh` も同じ約束を守る)
- 実在人物 personality cloning ← 同意なし不可、`serving/commercial_gate.assert_commercial_ready` で BLOCK
- deadbot ← 法整備未成熟、policy 層のみ

## 関連 memory link

- [[project_transfusion-gibson-oss-2026-05-17]]
- [[architecture_transfusion-gibson-blueprint-2026-05-17]]
- [[critical-rules-core]] R7 / R11 / R13 / R14 / R16 / R17
- [[feedback_no-permanent-claim-2026-05-14]]
- [[feedback_no-r-numbers-in-commits-2026-05-15]]
