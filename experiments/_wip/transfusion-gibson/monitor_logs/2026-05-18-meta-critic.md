# meta-critic audit — 2026-05-18 premise-doubt pass

Agent: `critic` (read-only, adversarial). Verdict: **REJECT → ADDRESSED**.

Pre-commitment scorecard: predicted 5 catastrophic/major findings, all 5 hit.

## CATASTROPHIC (prior audit overconfident)

1. **`THIRD_PARTY_NOTICES.md` parser extracts 0 entries.** Empirically verified: `_parse_red_from_notices()` on the real notices file returned `set()`. Regex required `**name**` bold bullets; every RED entry was plain text. Parser was theatrical — only `DEFAULT_RED_NAMES` actually blocked. **Severity: CRITICAL.** → **FIXED**: parser handles both bold + plain bullets, em-dash/en-dash/--, slash-alternation, paren aliases. Tests now exercise real notices and synthetic edits (test_license_guard.py:50-150).

2. **"65 tests pass" was happy-path heavy for the safety gates.** test_check_blocks_red_dep_override bypassed `_parse_red_from_notices` via the `red_names=` kwarg, hiding the parser bug. → **FIXED**: new tests `test_parser_lifts_real_notices_entries` and `test_check_blocks_synthetic_red_from_notices` exercise the parser end-to-end on disk.

3. **CI does NOT run torch-gated tests.** `.github/workflows/ci.yml:45` ran 5 of 8 test files. test_pgc_dfm.py, test_geometry.py, test_disentangle.py — the SPF Loss math, detach-basis-for-cond contract, orthogonality — never executed by CI. → **FIXED**: new `torch-tests` job installs CPU torch wheel and runs the three torch-gated suites on every push.

## PREMISE DOUBT — needs evidence

4. **`docs/persona-rfc.md` inconsistent with implementation semantics.** RFC line 31: "SHA-256 over the materialized payload"; impl: "8-hex prefix of weights-bundle sha256". Two different things hashed. → **FIXED**: RFC rewritten — `rev` is unambiguously "8-hex prefix of the SHA-256 of the persona's weights bundle (concatenation of all LoRA delta files in lexicographic filename order)". Cross-validation deferred to 0.2.0 with explicit note.

5. **toy_train.py target degeneracy.** `basis.detach()` passed to batch builder, but basis is in `Adam([basis], ...)` and is the target source — model learns per-persona mean, basis stays anywhere orthogonal. "Convergence" is mechanical. Not flagged in MODEL_CARD limitations. → **FIXED**: file docstring rewritten to lead with "WHAT THIS IS, AND WHAT IT IS NOT"; MODEL_CARD Limitations adds explicit disclosure.

6. **`placeholder-org` + arXiv:2512.07092 cite-as-real.** README cited the paper as real while REFERENCES.md flagged pending-human-verify; pyproject + MODEL_CARD had placeholder URLs. → **FIXED**: README citations now have `[unverified]` inline markers; USER_ACTIONS.sh sweeps pyproject + docs for placeholder-org rewrite.

## OK ON SECOND LOOK

- `detach_basis_for_cond` documented contract holds (ortho-term gradient flow is documented + tested separately).
- `_pkg_name` min-index fix correct for all edge cases tested.
- backbone re-import safe on CPU host (NotImplementedError only at `.load`/`.__call__`).
- `USER_ACTIONS.sh` sed -i.bak portable across GNU/BSD.

## ADDITIONAL FINDINGS

- `monitor_logs/` was empty (only README.md) — this audit's outputs are now persisted to 3 files (architect / verifier / meta-critic). The false-positive-incident lesson is now operationalized for THIS audit.

## VERDICT

**REJECT → ADDRESSED**. All 5 pre-committed predictions hit; all 5 closed in this audit pass. New tests cover parser + commercial-gate edge cases. Final state passes 85/85 tests, license_guard OK, check_file_lengths OK.
