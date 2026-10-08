# Security Policy

## Security model

This project separates governance, trust/execution, and performance concerns.

- OCI workload identity establishes the workload principal.
- OpenAI federation establishes the downstream trust relationship.
- Service-account and MCP/resource policy establish authority.
- Skills are privileged instructions/code and require inspection and approval.
- Prompt caching improves cost/latency but never establishes authority.

## Secrets

Do not commit or report:

- JWTs or access tokens
- authorization headers or cookies
- private keys or signer material
- customer records
- raw authorization context
- API keys or other credentials

## Reporting

For a suspected vulnerability, provide a minimal reproducible description without including credentials or sensitive data. Do not publish exploitable secrets in issues or pull requests.
