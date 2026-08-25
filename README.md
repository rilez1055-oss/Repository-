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

1. Repository and governance policy
2. OCI identity probe
3. Oracle JWT inspection
4. Workload-identity federation configuration
5. Negative federation tests
6. Dedicated OpenAI service-account authorization
7. Minimal Responses API call
8. MCP authorization layer
9. MCP tools
10. MCP App rendering
11. Workspace Agent trigger
12. End-to-end validation

## Gate philosophy

A gate is complete only when there is concrete evidence. An HTTP 200 alone does not establish identity correctness. Federation must also reject intentionally invalid claims such as an incorrect audience, expired token, missing required claim, or unauthorized workload identity.

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
│   └── tests/test_identity_probe.py
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
