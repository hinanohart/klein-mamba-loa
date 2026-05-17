# Contributing

`klein-mamba-loa` is pre-alpha. The contribution surface is limited
while the loss formulation is still hypothesis stage.

## Right now

- **Issues**: welcome — bug reports, license-map disputes, RFC comments
  on `docs/persona-rfc.md`.
- **Pull requests**: not yet open. The PR queue opens at the S2 → S3
  transition (see `experiments/_wip/transfusion-gibson/pipeline-state.json`).
- **Discussions**: GitHub Discussions if available on the host fork.

## License of contributions

By submitting a contribution you agree it is licensed under
Apache-2.0, identical to the rest of the repository.

## Anti-checklist

These are the things contributions **must not** do:

- introduce a runtime dependency on a RED-license model or library.
  `THIRD_PARTY_NOTICES.md` is the canonical list; `scripts/license_guard.py`
  enforces it in pre-commit and CI (`.github/workflows/ci.yml`).
- exceed the 500-line cap on a single Python file under
  `klein_mamba_loa/` or `scripts/`. `scripts/check_file_lengths.py`
  enforces this in pre-commit and CI; a deliberate cap-breaker is a
  sub-R14 trigger and must be flagged in the PR description.
- claim empirical results from the SPF formulation before S3 has
  produced 3 independent loss curves on the real Tier 1 stack (toy
  training under `examples/toy_train.py` is **not** scientific
  validation — see `docs/MODEL_CARD.md` Limitations).
- weaken or remove the code-layer erasure endpoint
  (`klein_mamba_loa/persona/erasure.py`); it is default-on by design.
- weaken `klein_mamba_loa/serving/commercial_gate.py`. The
  `missing-consent` warning from `validate_payload` MUST raise
  `CommercialDeploymentBlocked` on the commercial path.
- add tooling that infers consent silently — consent must be carried
  by the MCP `persona://` payload, never inferred.
- cite arXiv IDs from `docs/REFERENCES.md` that are still
  `status: pending-human-verify` in any external artifact (paper,
  README on a sister repo, blog). The `release-tag` step of
  `USER_ACTIONS.sh` refuses to cut a tag while any reference is
  still pending verification.

## Style

- Python 3.10+, type hints, ruff + mypy in CI.
- File size cap: a single Python file should not exceed 500 code
  lines (blank and pure-comment lines excluded — see
  `scripts/check_file_lengths.py`). Module-crossing structural
  changes require an explicit sub-R14 note in the PR.
- Tests under `tests/`, pytest, no network in test paths. Torch-only
  tests live in their own files (`tests/test_pgc_dfm.py`,
  `tests/test_geometry.py`, `tests/test_disentangle.py`) so the
  no-torch CI path stays runnable.

## Commit messages

- Imperative mood, present tense ("add SPF Loss", not "added").
- No issue-tracker-internal labels (e.g. internal rule numbers) in
  commit messages; describe the change in user-facing terms.

## Disclosures

Security and responsible-use disclosures go through the channel listed
in `SECURITY.md`. Do not file public issues for either category.
