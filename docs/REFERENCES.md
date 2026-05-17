# REFERENCES — retrieved-at evidence

This file is the single source of truth for the **foundational citations**
used by the SPF Loss formulation and the README. Every entry MUST include
the arXiv ID, the canonical URL, and the date on which the citation was
last verified. Before submitting arXiv preprint v1 the entries marked
`status: pending-human-verify` MUST be opened in a browser and the
abstract sha-256 (over the visible HTML body) MUST be recorded.

The auto-OSS pipeline cannot itself open arXiv URLs in a browser; the
WebSearch tool used during S0-a returned hits but does not capture a
content snapshot. Treat the abstract sha as a `USER_ACTIONS.sh` step.

## Format

```
ID         : <arXiv:NNNN.NNNNN>
Title      : <paper title>
Canonical  : <https://arxiv.org/abs/NNNN.NNNNN>
Retrieved  : <YYYY-MM-DD, by which agent or human>
Abstract   : <sha-256 of abstract body, first 16 hex chars>
Status     : pending-human-verify | verified
Used by    : <list of in-repo files that cite this ID>
```

## Entries

### arXiv:2408.11039 — Transfusion

```
ID         : arXiv:2408.11039
Title      : Transfusion: Predict the Next Token and Diffuse Images with One Multi-Modal Model
Canonical  : https://arxiv.org/abs/2408.11039
Retrieved  : 2026-05-17 (S0-a WebSearch; URL canonicalized, abstract not captured)
Abstract   : pending-human-verify
Status     : pending-human-verify
Used by    : klein_mamba_loa/flow/loss/pgc_dfm.py (doc), docs/MODEL_CARD.md, README.md
```

### arXiv:2512.07092 — The Geometry of Persona

```
ID         : arXiv:2512.07092
Title      : The Geometry of Persona: Disentangling Personality from Reasoning in LLMs
Canonical  : https://arxiv.org/abs/2512.07092
Retrieved  : 2026-05-17 (S0-a WebSearch; URL canonicalized, abstract not captured)
Abstract   : pending-human-verify
Status     : pending-human-verify
Used by    : klein_mamba_loa/flow/loss/pgc_dfm.py (doc), docs/MODEL_CARD.md, README.md
Note       : arXiv IDs of the form 25NN are valid only from 2025-12 onward.
             Today (2026-05-17) the ID-space is plausible but the paper's
             continued availability MUST be verified by a human reviewer
             before arXiv preprint v1 cites it.
```

### arXiv:2602.05214 — Disentangled Representation Learning via Flow Matching

```
ID         : arXiv:2602.05214
Title      : Disentangled Representation Learning via Flow Matching
Canonical  : https://arxiv.org/abs/2602.05214
Retrieved  : 2026-05-17 (S0-a WebSearch; URL canonicalized, abstract not captured)
Abstract   : pending-human-verify
Status     : pending-human-verify
Used by    : klein_mamba_loa/flow/loss/pgc_dfm.py (doc), docs/MODEL_CARD.md, README.md
```

### arXiv:1909.04076 — TIMETRAVEL

```
ID         : arXiv:1909.04076
Title      : Counterfactual Story Reasoning and Generation (TIMETRAVEL)
Canonical  : https://arxiv.org/abs/1909.04076
Retrieved  : 2026-05-17 (S0-a WebSearch)
Abstract   : pending-human-verify
Status     : pending-human-verify
Used by    : docs/MODEL_CARD.md (S4 eval seed)
```

### arXiv:2602.15669 — Persona-Flow (naming-collision-check only)

```
ID         : arXiv:2602.15669
Title      : Persona-Flow (OCEAN trait vector algebra)
Canonical  : https://arxiv.org/abs/2602.15669
Retrieved  : 2026-05-17 (R14 探索 freeze)
Abstract   : pending-human-verify
Status     : pending-human-verify
Used by    : project_transfusion-gibson-oss-2026-05-17.md memory (naming collision rationale)
Note       : NOT cited as foundation. Listed here so the SPF naming-collision
             argument is auditable: this paper uses Persona-Flow as an OCEAN
             trait vector algebra construct; SPF uses a velocity-field
             disentanglement construct. Citations of distinct contexts must
             coexist; abstract sha is required for the audit trail.
```

## Pre-arXiv-submit checklist

The following items are blocking for `arXiv preprint v1` (handled by
`USER_ACTIONS.sh` step 5):

- [ ] Open each `Canonical` URL above in a browser
- [ ] Confirm title matches the `Title` field exactly
- [ ] Save the abstract HTML body, compute sha-256, record the first 16
      hex chars in the `Abstract` field
- [ ] Flip `Status` from `pending-human-verify` to `verified`
- [ ] Commit this file as `docs: REFERENCES.md verified pre-arXiv-v1`
- [ ] Then proceed with arXiv submission
