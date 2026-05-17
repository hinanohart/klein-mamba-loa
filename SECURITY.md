# Security & Responsible Use Policy

## Scope

This policy covers (a) software security of the `klein-mamba-loa`
package itself and (b) responsible-use constraints around persona
features that are inseparable from the project's research direction.

## Reporting a vulnerability

For software vulnerabilities (RCE, supply-chain, etc.) please file a
**private** security advisory on the GitHub repository, or contact the
maintainers via the address listed in `pyproject.toml`.

For misuse reports (real-person clone without consent; deadbot abuse;
adversarial persona trace leakage), use the same channel and label the
report `responsible-use`.

## Threat model

This package is **research code**. It is not hardened against:

- Malicious model weights — pulling untrusted weight checkpoints is the
  caller's responsibility. We rely on `safetensors` to avoid pickle-based
  code execution but do not sandbox forward passes.
- Untrusted MCP servers — the `persona://` resource scheme expects a
  trusted MCP transport. Untrusted payloads can attempt to overwrite
  persona state.
- Side-channel attacks on persona orthogonality — the orthogonality
  regularizer reduces information leakage between persona strata but
  does NOT provide cryptographic guarantees.

## Persona / responsible use

1. **Real-person personality cloning** requires explicit subject consent.
   The MCP `persona://` payload's `consent.subject_consent_ref` field
   MUST be populated for any real-person persona. A missing value
   produces a `missing-consent` warning from
   `klein_mamba_loa.mcp.persona_scheme.validate_payload`, and
   `klein_mamba_loa.serving.commercial_gate.assert_commercial_ready`
   turns that warning into a hard `CommercialDeploymentBlocked`
   exception on the commercial path. Call `assert_commercial_ready`
   at the request boundary of any commercial deployment.

2. **Right to be forgotten** is implemented as a code-layer endpoint
   (`klein_mamba_loa/persona/erasure.py`), enabled by default. Scope at
   the current S1 release: the LoRA-pool directory
   `weights/lora_pool/<persona_id>/` is recursively deleted (all file
   types, not only `.safetensors`). **Mem0 namespace cleanup and
   LightRAG node-filter cleanup are NOT yet wired** (the adapters
   under `klein_mamba_loa.memory` are S2 work). `ErasurePlan.warnings`
   surfaces this gap, and `mem0_cleaned` / `lightrag_cleaned` flags on
   the returned plan are always `False` at S1. Operators relying on
   the endpoint today must also delete from Mem0/LightRAG manually.
   Backups outside this package are NOT covered.

3. **Deadbot (deceased-person persona) generation** is NOT gated by
   code. Jurisdictional legal review is the operator's responsibility.

4. **Adversarial-persona probe traces** must be released through an
   access-restricted channel only. Open release is forbidden.

## Secrets

Never commit `.env`, HuggingFace tokens, or any other credentials.
The `.gitignore` excludes the common patterns. CI should reject any
file matching `*.token`, `*.pem`, `id_rsa*`, `.env.*` (except
`.env.example`).

## Cryptography

No cryptographic primitives are exposed by this package. Persona
orthogonality is a learning-time regularizer, not a security primitive.
