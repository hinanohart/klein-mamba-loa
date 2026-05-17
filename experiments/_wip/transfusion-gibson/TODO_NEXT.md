# TODO_NEXT (top-3, auto-resume entry)

最終更新: 2026-05-17 / audit pass 完了 / Claude 自走範囲 = 完了 / 残りはすべて `USER_ACTIONS.sh` に集約

## P0 — 残り手動 (Claude 実行不可)

すべて `bash USER_ACTIONS.sh --plan` 参照。8 step を必要なものだけ走らせる。

1. `bash USER_ACTIONS.sh github-repo-create` — gh auth login 後に走らせる
2. `bash USER_ACTIONS.sh install-tier1` + `bash USER_ACTIONS.sh measure-vram` — GPU host で
3. `bash USER_ACTIONS.sh toy-train-3run` — S3 gate
4. `bash USER_ACTIONS.sh references-verify` — 人間が arXiv 3 本の abstract sha を埋める
5. `bash USER_ACTIONS.sh release-tag` — REFERENCES verified が前提
6. `bash USER_ACTIONS.sh arxiv-submit`

## P1 — Claude 側で着手可能 (新規 user directive 時)

- transfusion-pytorch (lucidrains) fork 要否再判定 (S3 結果が揃ってから)
- mamba_transfusion_bridge.py 具体 forward 実装 (S3 着手前)
- mem0 / lightrag adapter 実装 (`klein_mamba_loa/memory/`) → erasure mem0_cleaned / lightrag_cleaned を `True` 化
- backbone wrapper concrete load (S2 → S3 prep)

## /compact 跨ぎ recovery 手順

1. `~/.claude/projects/-home-runza/memory/architecture_transfusion-gibson-blueprint-2026-05-17.md` Read
2. `~/.claude/projects/-home-runza/memory/project_transfusion-gibson-oss-2026-05-17.md` Read
3. `~/oss/klein-mamba-loa/experiments/_wip/transfusion-gibson/pipeline-state.json` Read
4. `~/oss/klein-mamba-loa/experiments/_wip/transfusion-gibson/CONTEXT.md` Read
5. `cd ~/oss/klein-mamba-loa && bash USER_ACTIONS.sh --plan` で残り action 確認
