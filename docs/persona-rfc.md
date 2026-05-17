# RFC: MCP `persona://` resource scheme (draft 0.1.0)

This document is the standalone proposal for an MCP resource scheme that
carries persona state across hosts. It is decoupled from this OSS:
acceptance by the upstream MCP spec is **not** a prerequisite for this
package to function.

## Motivation

The MCP 2025-11-25 spec does not define a transport for persona /
agent-identity state. Existing options either piggyback persona on
tool-call arguments (lossy) or use bespoke side channels (incompatible
between agents). A first-class URI scheme has three benefits:

1. **Atomic possession handoff** — `possession.atomic = true` enables
   two-phase commit when transferring a persona between hosts.
2. **Consent transport** — `consent.subject_consent_ref` is in-band,
   so a downstream host can refuse to instantiate a real-person
   persona without an attached consent reference.
3. **Blend semantics** — `?blend=<float>` formalizes partial overlay
   of one persona by another.

## URI

```
persona://<persona_id>[@<namespace>][?rev=<sha256_8>&blend=<float>]
```

Grammar (enforced by the reference implementation):

- `persona_id`: `^[A-Za-z0-9_-]{1,64}$` — ASCII alphanumerics, hyphen,
  underscore; no dot, no slash, no whitespace, no leading dot.
- `namespace`: `^[A-Za-z0-9_.-]{1,64}$` — adds dot to the persona_id
  charset (e.g. `team.alpha`).
- `rev`: `^[0-9a-fA-F]{8}$` — 8-char (4-byte) lowercase-or-uppercase
  hex prefix of the **SHA-256 of the persona's weights bundle**
  (concatenation of all LoRA delta files in `weights/lora_pool/<persona_id>/`,
  in lexicographic filename order). This is the value the resource
  server hashes; payload-level `rev` MUST equal the URI-level `rev`
  when both are present.
- `blend`: float in `[0, 1]`.
- The URI MUST NOT carry a path component after the authority
  (`persona://x/y` is invalid — `y` is silently dropped by URI parsers
  unless the implementation rejects, as the reference implementation
  does).
- Query keys MUST appear at most once.

## Payload (JSON)

```json
{
  "persona_id": "...",
  "namespace": "...",
  "rev": "deadbeef",
  "consent": {
    "subject_consent_ref": "doc-uri-or-id",
    "real_person": false,
    "deadbot": false
  },
  "possession": { "atomic": true },
  "blend": 0.0,
  "loa_capabilities": ["..."],
  "memory_refs": ["mem0://...", "lightrag://..."]
}
```

Field semantics:

- `rev` (payload-level) is the same 8-hex weights-bundle SHA-256 prefix
  as the URI field; the validator does not currently cross-check
  payload-vs-URI `rev` (planned 0.2.0).
- `possession.atomic` must be a JSON boolean.
- `loa_capabilities` and `memory_refs` must be `array<string>`.

## Validation

`klein_mamba_loa.mcp.persona_scheme.validate_payload` returns a list of
warning strings. A warning whose substring begins with `missing-consent`
MUST be treated as a **block** for commercial deployment paths; the
reference implementation enforces this via
`klein_mamba_loa.serving.commercial_gate.assert_commercial_ready` which
raises `CommercialDeploymentBlocked`.

`PersonaURIError` is raised for malformed payloads: missing
`persona_id`, persona_id outside the regex, malformed `consent`,
non-bool `possession.atomic`, non-`array<string>` `loa_capabilities`
or `memory_refs`, blend out of range, or `rev` outside the 8-hex
format.

## Reference implementation

`klein_mamba_loa/mcp/persona_scheme.py` (this repository), Apache-2.0.

## Open questions

- transport binding: SSE vs. WebSocket. Defer to the MCP transport WG.
- revocation cascade: how does an MCP resource server propagate a
  revoked `subject_consent_ref` to downstream caches? Out of scope
  for 0.1.0-draft.
- session-bound vs. agent-bound personas: the draft treats personas
  as orthogonal to sessions; refinement is welcome.
- payload-vs-URI `rev` cross-validation: deferred to 0.2.0 once the
  MCP transport WG fixes whether the URI hash should canonicalise
  weights-bundle order or rely on a manifest.

## Status

`0.1.0-draft`. The reference implementation enforces:

- grammar above for `persona://` URIs
- payload schema (persona_id, namespace, rev, consent, possession,
  blend, loa_capabilities, memory_refs)
- `missing-consent` warning surfacing for real_person / deadbot
  payloads lacking `subject_consent_ref`

Wire-format compatibility shims with the MCP SDK land at S5 of this
project's pipeline.
