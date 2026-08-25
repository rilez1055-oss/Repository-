# Security

This repository demonstrates a layered agent-security reference architecture.

## Security model

1. **Authentication:** OCI workload identity establishes the machine principal.
2. **Federation:** OpenAI workload identity federation establishes whether that principal is trusted.
3. **Authorization:** A dedicated OpenAI service account defines permitted API capabilities.
4. **Tool authorization:** MCP/server-side policy independently authorizes each operation.
5. **Resource authorization:** Privileged operations are constrained to the specific business resource being accessed.
6. **Presentation:** MCP Apps are presentation only and are never authoritative for business state.

## Required invariant

> Instructions, model output, UI state, and tool arguments are never security boundaries.
> Authentication comes from workload identity. Authorization comes from independent server-side policy.
> Every privileged operation must be authorized again at execution time.

## Credential handling

- No long-lived OpenAI API credential belongs in the OCI workload when workload identity federation is available and configured for the deployment.
- Oracle and OpenAI tokens must not be logged or persisted.
- Configuration files containing identifiers should use placeholders or environment-provided values.
- Negative tests must demonstrate rejection of invalid identity claims.

## Security reporting

Do not disclose suspected vulnerabilities publicly before coordinated remediation. Report security issues privately to the repository owner through an appropriate private GitHub security channel when enabled.
