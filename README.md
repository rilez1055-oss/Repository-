# OCI → OpenAI Reference Architecture

A security-first reference implementation for an OCI workload identity → Oracle Identity Domain → OpenAI federation → Responses/MCP/Skills execution path.

## Execution gates

| Gate | Boundary | State |
|---|---|---|
| 1 | OCI metadata / instance identity | 🟡 runtime evidence required |
| 2 | JWT claim validation | 🟡 runtime/cryptographic evidence required; local inspector is non-verifying |
| **3** | **OCI Instance Principal → Oracle Identity Domain token** | **🟡 ACTIVE — requires OCI runtime evidence** |
| 4 | Oracle token → OpenAI WIF | ⏳ |
| 5 | WIF → dedicated service-account authorization | ⏳ |
| 6 | Service account → Responses API | ⏳ |
| 7 | MCP authorization | ⏳ |
| 8 | Skills / shell execution | ⏳ |
| 9 | MCP App | ⏳ |
| 10 | Workspace Agent | ⏳ |
| 11 | End-to-end | ⏳ |

**No gate is marked PASS because code exists. A gate is PASS only after its boundary has been exercised and non-secret evidence has been recorded.**

## Gate 3

Run `scripts/gate3_token_exchange.py` **inside the OCI Compute workload**. It requires `OCI_IDENTITY_DOMAIN_URL` and an OCI Instance Principal. `OCI_IDENTITY_DOMAIN_SCOPE` is optional and defaults to `urn:opc:idm:__myscopes__`; set it when the Identity Domain configuration requires a different scope.

Success output is intentionally limited to:

```text
Oracle token acquired: YES
Token length: <number>
Token persisted: NO
```

Never print the JWT, bearer token, authorization headers, cookies, signer material, or the complete HTTP response. The token is held only in process memory.

For the next diagnostic step, run the exchange and claim inspection in one process:

```bash
python scripts/gate3_token_exchange.py --inspect-claims
```

This avoids the unsafe pattern of echoing a live bearer token merely to pipe it into another process.

### Failure classification

- `401` / `403`: Instance Principal or Oracle authorization/configuration boundary.
- DNS / connection / timeout: OCI → Identity Domain network path.
- Signer initialization failure: OCI Instance Principal / SDK environment.
- Successful HTTP response without `access_token`: token-exchange configuration/response problem.
- Oracle token succeeds but OpenAI later rejects it: Gate 3 remains PASS; investigate Gate 4.

## Claim inspection

`scripts/inspect_oracle_jwt.py` performs **local, non-verifying JWT payload decoding** only. Decoding is not signature verification and is never treated as proof of trust. The inspector prints claim presence/type and selected safe structural metadata; it never prints the token.

A structural decode is therefore diagnostic evidence, not Gate 2 cryptographic validation evidence.

## Trust plane vs performance plane

```text
TRUST / EXECUTION
OCI workload identity
        ↓
OpenAI federation
        ↓
service-account authorization
        ↓
Responses execution
        ↓
MCP server authz
        ↓
resource-level authz
        ↓
real systems

PERFORMANCE
rendered context
        ↓
stable prefix
        ↓
explicit cache breakpoint
        ↓
prompt cache
```

**Cache state never becomes evidence of authority.** Every privileged MCP operation independently evaluates `principal + action + resource + current policy` at the authoritative server boundary.

## Deterministic context generation

The future cacheable prefix is modeled as versioned components:

```text
agent-policy-v1
reference-set-v3
mcp-tools-v2
response-policy-v1
        ↓
canonical rendering
        ↓
stable-prefix digest
        ↓
explicit cache breakpoint
        ↓
prompt cache
```

Dynamic data stays outside the stable prefix whenever possible: request-specific authorization context, current resources, timestamps, transient tool results, and user input.

The repository contains pure caching utilities and tests, but does **not** enable live OpenAI calls or WIF integration before Gate 3 evidence exists.

### Current GPT-5.6 cache contract

The current API reference documents `prompt_cache_key` and `prompt_cache_options` for GPT-5.6+, with `mode: "explicit"` disabling the implicit breakpoint, `ttl: "30m"` as the currently supported TTL, up to four explicit writes per request, and matching against up to 80 recent breakpoints. The cache key is limited to 64 characters. These are implementation details, not security controls.

## Skills security

Skills are an execution/input trust boundary, not merely prompt text. A Skill bundle must be inspected and approved before use. Do not expose an arbitrary open Skill catalog to end users. Pin approved versions and review `SKILL.md`, bundled files, dependencies, network behavior, and write/high-impact capabilities.

Skills do not establish authorization. A Skill instruction cannot authorize an MCP action or resource operation.

## Observability

Allowed aggregate telemetry:

- `input_tokens`
- `cached_tokens`
- `cache_write_tokens`
- `uncached_input_tokens`
- latency
- cache-hit ratio
- estimated input cost
- model
- agent version
- tool schema version

Never record JWTs, authorization headers, prompt contents, customer records, raw authorization context, or secrets.

## Current OpenAI implementation posture

The eventual API integration should use the Responses API. Current OpenAI documentation supports GPT-5.6-family Responses workflows, prompt-cache keys/options, explicit cache breakpoints, and versioned hosted Skills. Implementation details should be re-verified against the current API reference when Gate 4/6 opens.

## Repository status

This branch contains the offline/testable foundation and Gate 3 acceptance tooling. It does not claim live OCI, WIF, Responses, MCP, or Skills execution. Gate 3 remains blocked on OCI runtime evidence.
