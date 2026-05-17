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

- `persona_id`: ASCII, no `/`, must not start with `.`
- `namespace`: optional logical bucket
- `rev`: 8-char prefix of SHA-256 over the materialized payload
- `blend`: `[0, 1]`

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

## Validation

`klein_mamba_loa.mcp.persona_scheme.validate_payload` returns a list of
warning strings. A warning whose substring is `missing-consent` MUST
be treated as a **block** for commercial deployment paths.

A `PersonaURIError` is raised for malformed payloads (missing
`persona_id`, malformed `consent`, blend out of range).

## Reference implementation

`klein_mamba_loa/mcp/persona_scheme.py` (this repository), Apache-2.0.

## Open questions

- transport binding: SSE vs. WebSocket. Defer to the MCP transport WG.
- revocation cascade: how does an MCP resource server propagate a
  revoked `subject_consent_ref` to downstream caches? Out of scope
  for 0.1.0-draft.
- session-bound vs. agent-bound personas: the draft treats personas
  as orthogonal to sessions; refinement is welcome.

## Status

`0.1.0-draft`. The reference implementation is feature-complete
for the parser and validator. Wire-format compatibility shims with
the MCP SDK land at S5 of this project's pipeline.
