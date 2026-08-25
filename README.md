# OCI → OpenAI Reference Architecture

A security-first reference implementation for an OCI workload identity → Oracle Identity Domain → OpenAI federation → Responses/MCP/Skills execution path.

## Execution gates

| Gate | Boundary | State |
|---|---|---|
| 1 | OCI metadata / instance identity | 🟡 runtime evidence required |
| 2 | JWT structural / claim validation | 🟢 local test substrate |
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

Run `scripts/gate3_token_exchange.py` **inside the OCI Compute workload**. It requires `OCI_IDENTITY_DOMAIN_URL` and an OCI Instance Principal.

Success output is intentionally limited to:

```text
Oracle token acquired: YES
Token length: <number>
Token persisted: NO
```

Never print the JWT, bearer token, authorization headers, cookies, signer material, or the complete HTTP response.

The script does not persist the token. The token remains process-local and is discarded when the process exits.

### Failure classification

- `401` / `403`: Instance Principal or Oracle authorization/configuration boundary.
- DNS / connection / timeout: OCI → Identity Domain network path.
- Signer initialization failure: OCI Instance Principal / SDK environment.
- Successful HTTP response without `access_token`: token-exchange configuration/response problem.
- Oracle token succeeds but OpenAI later rejects it: Gate 3 remains PASS; investigate Gate 4.

## Claim inspection

After Gate 3 passes, pipe the freshly acquired token directly into `scripts/inspect_oracle_jwt.py`. The inspector performs **local, non-verifying JWT payload decoding** only. Decoding is not signature verification and is never treated as proof of trust.

The inspector prints claim presence/type and selected safe structural metadata by default. It does not print the token.

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

The repository includes pure caching utilities and tests, but does **not** enable live OpenAI calls or WIF integration before Gate 3 evidence exists.

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

The eventual API integration should use the Responses API. Current OpenAI documentation supports GPT-5.6-family Responses workflows, prompt-cache keys/options, explicit cache breakpoints, and versioned hosted Skills. Implementation details should be re-verified against the current API reference when Gate 6 is opened.

## Repository status

This branch intentionally contains the offline/testable foundation and Gate 3 acceptance tooling. It does not claim live OCI, WIF, Responses, MCP, or Skills execution.
