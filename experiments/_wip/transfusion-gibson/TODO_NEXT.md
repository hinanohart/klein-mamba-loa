# TODO_NEXT (top-3, auto-resume entry)

最終更新: 2026-05-17 / S0-S2 + S5(CPU) GREEN、S3-S4 GPU host gate

## P0 — user 介入必須 (Claude 自動進行対象外)

1. **GPU host へ checkout** + `pip install -e .[flow,mamba,flux]` + `python scripts/measure_vram.py --tier 1` で **real VRAM 測定**。結果 18-24 GB 圏に入れば GREEN、超過は Tier 再定義 trigger ([[architecture_transfusion-gibson-blueprint-2026-05-17]] § 3)。
2. **S3 toy training (3 run)**: `examples/toy_train.py` (まだ未作成、S3 で書く) で TIMETRAVEL subset 1k 件 + persona basis 4 で 1k step、loss curve 平均下降確認、`angular_orthogonality >= 0.7` check。
3. **GitHub remote 設定** (任意): `gh auth login` → `gh repo create klein-mamba-loa --public --source=. --push`。HF token 等は env var 経由のみ。

## P1 — Claude 側で進行可能 (新規 user directive 受領時)

- transfusion-pytorch (lucidrains) 公式 fork 要否再判定 (blueprint § 11 critic 残課題)
- mamba_transfusion_bridge.py 具体実装 (S2 stub → S3 用)
- examples/toy_train.py 雛形作成 (S3 GPU host で動かす前提の harness)
- docs/persona-rfc.md を MCP spec PR 用 standalone fork 化

## P2 — release 直前

- MODEL_CARD の training-data セクション最終化
- CHANGELOG → 0.1.0 release entry
- release tag (user-intervention point、Claude は実行しない)
- arXiv preprint v1 投稿 (user-intervention point)

## /compact 跨ぎ recovery 手順

1. `~/.claude/projects/-home-runza/memory/architecture_transfusion-gibson-blueprint-2026-05-17.md` Read
2. `~/.claude/projects/-home-runza/memory/project_transfusion-gibson-oss-2026-05-17.md` Read
3. `~/oss/klein-mamba-loa/experiments/_wip/transfusion-gibson/pipeline-state.json` Read
4. `~/oss/klein-mamba-loa/experiments/_wip/transfusion-gibson/CONTEXT.md` Read
5. `git -C ~/oss/klein-mamba-loa log --oneline` で commit 一覧確認
6. `next_action` 実行 (現在は USER ACTIONS 待ち)
