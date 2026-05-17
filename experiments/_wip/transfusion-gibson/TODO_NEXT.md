# TODO_NEXT (top-3 only, auto-resume entry)

## P0 — 本 turn または次 turn 即着手

1. **S0-c VRAM stub commit** + S0 → S1 transition (S0-c は GPU 実測 user 側のため structure-only GREEN とする)
2. **Phase 2 file batch を kluster verify** (LICENSE / pyproject.toml / README.md / scripts/measure_vram.py / state file / ethics gate stub)
3. **S1 scaffold 残**: THIRD_PARTY_NOTICES.md / SECURITY.md / MODEL_CARD draft / persona/erasure.py stub / mcp/persona_scheme.py stub

## P1 — S2 着手前

- `transfusion-pytorch` (lucidrains) production-grade 評価、fork 要否判断 (blueprint § 11 critic 残課題)
- `gh repo search klein-mamba-loa` 実行 (gh auth 必要)、SPF/KML 名称の追加 grep verify
- Mem0 + LightRAG の minimal install dry-run、`klein-mamba-loa[memory]` extras dep が破綻しないか確認

## P2 — S2 中

- `klein_mamba_loa/flow/loss/pgc_dfm.py` 実装 (≤500 行、sub-R14 trigger 回避)
- `klein_mamba_loa/persona/geometry.py` 直交 basis 実装
- `klein_mamba_loa/backbone/mamba_transfusion_bridge.py` adapter 実装
- unit test (gradient finite check、orthogonality > 0.7)
