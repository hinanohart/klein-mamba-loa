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

- introduce a runtime dependency on a RED-license model or library
  (`THIRD_PARTY_NOTICES.md` lists them; the planned `scripts/license_guard.py`
  will enforce this in CI)
- claim empirical results from the SPF formulation before S3 has
  produced 3 independent loss curves
- weaken or remove the code-layer erasure endpoint
  (`klein_mamba_loa/persona/erasure.py`); it is default-on by design
- add tooling that infers consent silently — consent must be carried
  by the MCP `persona://` payload, never inferred

## Style

- Python 3.10+, type hints, ruff + mypy in CI.
- File size cap: a single Python file should not exceed 500 lines
  unless the change is module-crossing and surfaced explicitly in
  the PR description (sub-R14 trigger; see `docs/ARCHITECTURE.md`).
- Tests under `tests/`, pytest, no network in test paths.

## Commit messages

- Imperative mood, present tense ("add SPF Loss", not "added").
- No issue-tracker-internal labels (e.g. internal rule numbers) in
  commit messages; describe the change in user-facing terms.

## Disclosures

Security and responsible-use disclosures go through the channel listed
in `SECURITY.md`. Do not file public issues for either category.
