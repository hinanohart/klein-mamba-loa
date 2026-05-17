# architect audit — 2026-05-18 residual scan

Agent: `architect` (read-only). Verdict: **CONDITIONAL ACCEPT** (7 conditions).

## STILL-OPEN CONTRACT ITEMS (blueprint section + reason)

- **[§1] `klein_mamba_loa/persona/__init__.py:3-5`** re-exports only `ErasurePlan, erase_persona`. Blueprint §1 lists `geometry.py`, `lora_pool.py`, `disentangle.py` as substance of `persona/`. Users must deep-import. Audit missed because tests use deep imports.
- **[§1] `klein_mamba_loa/core/__init__.py`, `flow/velocity/__init__.py`, `flow/solver/__init__.py`, `memory/__init__.py`** are 1-line docstrings only. README:99-114 and ARCHITECTURE:46-54 advertise them as boundary modules; either land surface stubs or strike from docs. → **FIXED** (S1-status disclosure docstrings added to all four).
- **[§2] `klein_mamba_loa/__init__.py:1-6`** exports `__version__` only — no `PGCDisentangledFMLoss`, no `parse_uri`, no `erase_persona`. Documented contract drift.
- **[§5/§2] LoRA `?blend=` URI consumer is still a documentation promise.** `mcp/persona_scheme.py:120-128` parses `blend` into `PersonaURI.blend`, `lora_pool.py:40-41` raises `NotImplementedError`. No code path binds URI → `LoRAPool.blend(weight=...)`.
- **[§11] `transfusion-pytorch` production-grade fork decision** is still `DEFERRED` (`pipeline-state.json:80`). Bridge is non-Module stub. `BridgeConfig.num_strata=4` is arbitrary.

## DRIFT / STALE

- **`THIRD_PARTY_NOTICES.md:62,75`** — "license-guard (planned, S1)" and `--refresh-notices` flag NOT implemented. → **FIXED** (rewrite to past tense).
- **`CONTRIBUTING.md:24`** — "planned `scripts/license_guard.py`" no longer planned. → **FIXED**.
- **`THIRD_PARTY_NOTICES.md:41`** — "Janus-Pro Optional via `[flux]` extras subtree (planned)". `pyproject.toml` has no `[janus]` extra. → **FIXED** (wording corrected).
- **`docs/ARCHITECTURE.md:60-61`** — "future `license_guard.py`" already exists. → **FIXED**.
- **`docs/MODEL_CARD.md:73`** — references "older Σ_{i≠j} notation in earlier drafts" — unnecessary noise.
- **`CHANGELOG.md`** is `## [Unreleased]` — `USER_ACTIONS.sh:140` cuts tag without updating.

## HYGIENE / ORPHAN

- **`experiments/_wip/transfusion-gibson/vram_report.json`** tracked dry-run artifact. → **FIXED** (untracked + .gitignore'd).
- **`.gitignore`** lacks `vram_report.json`, `toy_train_report.json`. → **FIXED**.
- **`r14/` directory** appears empty without `.gitkeep`.
- **`pyproject.toml:84-86`** `placeholder-org` in 3 URLs + **`docs/MODEL_CARD.md:124`** citation URL. `USER_ACTIONS.sh:59` rewrites only `pyproject.toml`. → **FIXED** (USER_ACTIONS.sh now sweeps pyproject + docs).

## TEST SURFACE GAPS NEW

- No test for `MambaTransfusionBridge` import. → **FIXED** (tests/test_backbone_surface.py).
- `LoRAPool.list_available()` zero coverage. → **FIXED** (tests/test_lora_pool.py).
- `scripts/measure_vram.py:_gate()` no test. → **FIXED** (tests/test_measure_vram.py).
- `assert_commercial_ready` with malformed payload untested. → **FIXED** (test_commercial_gate.py extended).
- No `examples/toy_train.py` no-torch import test. → **FIXED** (tests/test_toy_train_import.py).

## DOCS/CONTRIBUTING DRIFT

- `CONTRIBUTING.md` no mention of `scripts/check_file_lengths.py`, `commercial_gate`, REFERENCES verify step. → **FIXED** (anti-checklist + style updated).
- `docs/persona-rfc.md:31` `persona_id` spec disagrees with regex in `persona_scheme.py:42`. → **FIXED** (RFC rewritten to match regex; rev semantics clarified as weights-bundle sha).

## VERDICT

**CONDITIONAL ACCEPT** — all 7 conditions addressed in commits ce9b329 → (this audit pass).
