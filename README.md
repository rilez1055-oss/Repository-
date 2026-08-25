# OpenAI + OCI Agent Reference

A deliberately small reference system for demonstrating:

**workload identity → federation → least-privilege authorization → model execution → independently authorized tools → optional UI → asynchronous orchestration**

This repository is a reference implementation, not a claim that every provider-specific detail is universally supported. Provider-specific behavior must be verified against current documentation before deployment.

## Security invariant

Model instructions are not authorization.
Model output is not authorization.
UI state is not authorization.
Tool arguments are not authorization.
Authentication is established by workload identity.
Authorization is established independently by server-side policy.
Every privileged operation is authorized again at the point where it executes.

## Implementation gates

| Gate | Stage | Status |
|---|---|---|
| 1 | OCI identity acquisition | **Implemented; live OCI evidence pending** |
| 2 | Oracle JWT inspection | **Implemented; live OCI evidence pending** |
| 3 | Workload-identity federation configuration | Pending |
| 4 | Negative federation tests | Pending live provider test |
| 5 | Dedicated OpenAI service-account authorization | Pending |
| 6 | Minimal Responses API call | Pending |
| 7 | MCP authorization layer | Pending |
| 8 | MCP tools | Pending |
| 9 | MCP App rendering | Pending |
| 10 | Workspace Agent trigger | Pending |
| 11 | End-to-end validation | Pending |

The numbering above is intentionally shorter than the original planning list: the first live boundary is now represented by executable Gate 1/2 code, while provider configuration remains a separate later gate.

## Gate philosophy

A gate is complete only when there is concrete evidence. An HTTP 200 alone does not establish identity correctness. Federation must also reject intentionally invalid claims such as an incorrect audience, expired token, missing required claim, or unauthorized workload identity.

## Gate 1 / Gate 2 quick start

On an OCI Compute instance configured for Instance Principals:

```bash
export OCI_IDENTITY_DOMAIN_URL="https://<your-identity-domain>"
python identity-probe/src/run_probe.py
```

The command prints only redacted identifiers and non-secret claim metadata. It never prints or persists the Oracle access token.

See [`docs/identity.md`](docs/identity.md) for the exact gate criteria.

## Repository layout

```text
openai-oci-agent-reference/
├── AGENTS.md
├── README.md
├── SECURITY.md
├── pyproject.toml
├── .gitignore
├── identity-probe/
│   ├── AGENTS.md
│   ├── src/identity_probe.py
│   ├── src/oci_identity.py
│   ├── src/run_probe.py
│   └── tests/
├── federation/
│   ├── AGENTS.md
│   ├── config/
│   ├── src/claims.py
│   ├── src/validator.py
│   └── tests/
├── openai-client/
│   ├── AGENTS.md
│   ├── src/client.py
│   └── tests/
├── mcp-server/
│   ├── AGENTS.md
│   ├── server/
│   │   ├── auth/
│   │   ├── policy/
│   │   └── tools/
│   └── tests/
├── workspace-agent/
│   ├── AGENTS.md
│   ├── src/
│   └── tests/
└── docs/
    ├── architecture.md
    ├── identity.md
    ├── federation.md
    ├── authorization.md
    └── operations.md
```

## Important implementation rule

Provider-specific claim names, token endpoints, SDK constructors, model identifiers, and agent APIs are intentionally not hard-coded until verified against current provider documentation. The portable security model is the stable part of this repository.
