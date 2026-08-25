# Agent Instructions

## Security invariant

Model instructions are not authorization.
Model output is not authorization.
UI state is not authorization.
Tool arguments are not authorization.
Authentication is established by workload identity.
Authorization is established independently by server-side policy.
Every privileged operation is authorized again at the point where it executes.

## Security rules

- Never print, persist, or transmit access tokens.
- Never commit credentials, private keys, tokens, or secrets.
- Treat identity claims as untrusted input until cryptographically and semantically verified.
- Fail closed when required identity claims are absent or invalid.
- Do not modify cloud IAM or OpenAI authorization configuration automatically.
- Prefer the narrowest workload identity and service-account scope that satisfies the deployment.
- Perform resource-level authorization for privileged business operations.
- Keep UI state separate from authoritative business state.
- Tests must include negative authorization and federation cases.

## Development rules

- Keep provider-specific implementation isolated behind small interfaces.
- Do not assume undocumented model names, authentication flows, or claim names.
- Verify current provider documentation before relying on provider-specific behavior.
- Run unit tests before declaring a gate complete.
- Never claim a security gate passed without concrete test evidence.
