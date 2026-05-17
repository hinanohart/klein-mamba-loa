# Changelog

All notable changes are tracked here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added — residual audit pass (2026-05-18)

- `tests/test_backbone_surface.py`, `tests/test_lora_pool.py`,
  `tests/test_measure_vram.py`, `tests/test_toy_train_import.py` —
  surface-import tests so the no-torch CI path covers every wrapper.
- `klein_mamba_loa/core/`, `flow/velocity/`, `flow/solver/`,
  `memory/` — S1-status disclosure docstrings (was 1-line "S2 wiring"
  comments that didn't disclose the empty-package state).
- README: "Concept naming disclaimer" paragraph (Gibson many-to-many,
  Persona Vector ≠ Dixie Flatline, LoRA hot-swap ≠ Loa possession);
  `[unverified]` inline markers on the three foundation arXiv IDs.
- `MODEL_CARD.md` Limitations: explicit toy_train.py degeneracy note
  + Gibson concept-mapping bullet.
- `experiments/_wip/transfusion-gibson/monitor_logs/2026-05-18-*.md`
  persisted outputs from the 3 audit agents (architect / verifier /
  meta-critic) so future audits can compare.
- `.github/workflows/ci.yml` `torch-tests` job: installs CPU torch
  wheel and runs `test_pgc_dfm.py / test_geometry.py / test_disentangle.py`
  on every push.

### Changed — residual audit pass (2026-05-18)

- `scripts/license_guard.py`: parser now handles BOTH bold
  (`- **name**`) and plain (`- name`) bullet styles, em-dash /
  en-dash / `--` separators, slash-alternation, and parenthetical
  aliases. Previous regex matched zero entries in the real notices
  file; the "single source of truth" claim was theatrical. Comparison
  is now PEP 503 canonical (`flow_matching` ↔ `flow-matching`).
- `tests/test_license_guard.py`: new tests for the parser
  (`test_parser_lifts_real_notices_entries`,
  `test_parser_handles_both_bullet_styles`,
  `test_check_blocks_synthetic_red_from_notices`) so a future
  parser regression is loud.
- `docs/persona-rfc.md`: `persona_id` grammar tightened to
  `^[A-Za-z0-9_-]{1,64}$` (matches implementation), `rev` semantics
  unambiguously stated as 8-hex prefix of the LoRA-bundle SHA-256,
  query-key uniqueness + path-after-authority rejection documented,
  payload schema cross-typed.
- `examples/toy_train.py` + `docs/MODEL_CARD.md`: explicit
  "structural smoke test, not scientific validation" disclosure
  because the synthetic batch sources targets from the basis itself.
- `USER_ACTIONS.sh github-repo-create`: now sweeps `pyproject.toml`,
  `docs/MODEL_CARD.md`, `README.md`, `docs/REFERENCES.md` for
  `placeholder-org` (was pyproject only — MODEL_CARD citation would
  have leaked the placeholder into arXiv v1).
- `THIRD_PARTY_NOTICES.md`: stale "planned" wording replaced with
  the live state; `--refresh-notices` claim removed.
- `CONTRIBUTING.md`: anti-checklist now mentions the 500-LOC cap
  (with `check_file_lengths.py` reference), the commercial gate
  (`assert_commercial_ready`), and the REFERENCES-verify gate.
- `docs/ARCHITECTURE.md` module-boundary table: each module now
  marks its **S1 status** (live vs surface stub vs empty package)
  so readers don't expect substance that doesn't exist yet.
- `.gitignore`: `experiments/_wip/*/vram_report.json` and
  `toy_train_report.json` ignored; the tracked dry-run artifact
  was untracked (was always-modified-after-first-run).

## [Unreleased earlier]

### Added — audit pass (2026-05-17)

- `klein_mamba_loa/backbone/mamba2_wrapper.py`,
  `flux2_klein_wrapper.py`, `janus_pro_wrapper.py`: surfaces so the
  Tier 1 matrix references real symbols.
- `klein_mamba_loa/serving/commercial_gate.py`:
  `assert_commercial_ready` turns the `missing-consent` warning into
  a hard `CommercialDeploymentBlocked` exception on the commercial path.
- `scripts/check_file_lengths.py`: sub-R14 500-LOC trigger guard,
  wired into pre-commit and CI.
- `docs/REFERENCES.md`: arXiv retrieved-at evidence file (entries
  start `pending-human-verify`; `USER_ACTIONS.sh references-verify`
  is the flip).
- `examples/toy_train.py`: S3 toy-training scaffold (CPU-importable,
  GPU-runnable).
- `USER_ACTIONS.sh`: one-script bundle of every remaining manual step
  (gh repo create, HF login, GPU install, real VRAM, S3 toy train,
  REFERENCES verify, release tag, arXiv submit).
- `experiments/_wip/transfusion-gibson/{monitor_logs,failures}/`:
  audit-log and R8 failure-parking directories.
- Tests: `test_pgc_dfm.py`, `test_geometry.py`, `test_disentangle.py`,
  `test_license_guard.py`, `test_commercial_gate.py`; existing tests
  expanded with `rev` format, path-after-authority, recursive erasure,
  invalid-id charset, under-provisioned VRAM, and config-validation
  cases.

### Changed — audit pass (2026-05-17)

- `klein_mamba_loa/flow/loss/pgc_dfm.py`: orthogonality penalty
  switched from `Σ_{i≠j}` (each pair counted twice) to the equivalent
  unordered `Σ_{i<j}` form (each pair counted once); conditional CE
  term computed via basis-projection so no external classifier head
  is required, and `detach_basis_for_cond` is now actually honoured
  on the internal path.
- `klein_mamba_loa/persona/erasure.py`: now `rglob`s and `shutil.rmtree`s
  the persona directory (was shallow `.safetensors` glob with silent
  rmdir failure). `ErasurePlan` adds `mem0_cleaned`, `lightrag_cleaned`,
  and `warnings` to disclose the S2-pending adapters honestly. ID
  validation tightened to `^[A-Za-z0-9_-]{1,64}$`.
- `klein_mamba_loa/mcp/persona_scheme.py`: strict `persona_id` /
  `namespace` regex, `rev` validated as 8-hex sha prefix, path-after-
  authority rejected, duplicate query keys rejected, payload validator
  now checks `possession.atomic`, `loa_capabilities`, `memory_refs`.
- `klein_mamba_loa/eval/runtime_gate.py`: `RuntimeGateConfig` now
  validates `ortho_threshold ∈ [0,1]`, `vram_target_gb > 0`, and
  rejects negative tolerances / improvement floors.
- `klein_mamba_loa/persona/disentangle.py`: metric uses strict-upper
  triangular sum so it is unaffected by near-zero rows whose diagonal
  Gram entry slips below 1.
- `scripts/license_guard.py`: parses the RED section of
  `THIRD_PARTY_NOTICES.md` in addition to the hardcoded set; UTF-8
  read explicit; `_pkg_name` now uses min-index across all separators
  (the previous order-of-iteration logic mis-parsed env-marker
  specifications like `bar ; python_version<'3.11'`).
- `pyproject.toml`: `torch` moved out of core dependencies into
  `[flow]` / `[mamba]` / `[flux]` extras so CPU-only S0 / CI runs
  do not pull an 800 MB torch wheel. Authors / placeholder repo URL
  set; `[all]` extra now includes `[serving]`.
- `.github/workflows/ci.yml`: installs `[dev,mcp]` only on the core
  path, runs `license_guard`, `check_file_lengths`, `ruff`, `ruff
  format --check`, lenient `mypy`, pytest on the no-torch suite.
- `README.md`, `SECURITY.md`, `docs/MODEL_CARD.md`: erasure scope
  corrected (LoRA-only at S1; Mem0/LightRAG land at S2); consent
  BLOCK now references the actual `commercial_gate.assert_commercial_ready`
  code path; S0-c status uniformised to `DEFERRED to GPU host`.

### Pending (gated)

- S3 integration toy on the real Tier 1 stack (Mamba-2 + FLUX.2 klein
  + SPF Loss) — `USER_ACTIONS.sh toy-train-3run`.
- S4 small-scale eval against TIMETRAVEL branching ECE — depends on
  S3.
- Real VRAM measurement — `USER_ACTIONS.sh measure-vram`.
- `gh repo search` against the four naming axes — pending `gh auth`
  / `USER_ACTIONS.sh github-repo-create`.
- Release tag — `USER_ACTIONS.sh release-tag` (refuses while
  REFERENCES.md still has `pending-human-verify`).
- arXiv preprint v1 submit — `USER_ACTIONS.sh arxiv-submit`.

## [0.0.1.dev0] — initial scaffold

### Added

- S0 + S1 scaffold: Apache-2.0 LICENSE, NOTICE, SECURITY.md,
  THIRD_PARTY_NOTICES.md, pyproject.toml, README, .gitignore.
- `klein_mamba_loa/persona/erasure.py`: default-on right-to-be-forgotten
  endpoint (shallow LoRA glob — superseded in audit pass).
- `klein_mamba_loa/mcp/persona_scheme.py`: `persona://` URI parser
  and payload validator (0.1.0-draft — tightened in audit pass).
- `scripts/measure_vram.py`: S0-c VRAM measurement stub.
- S2 SPF Loss core: `PGCDisentangledFMLoss`, `SPFLossConfig`,
  `SPFLossOutput`, `orthogonality_penalty`, persona basis builder,
  angular orthogonality metric, Mamba-Transfusion bridge surface,
  runtime gate (superseded in audit pass).
- S5 release-prep documentation: MODEL_CARD, ARCHITECTURE,
  persona-rfc, CONTRIBUTING, CI configuration.
