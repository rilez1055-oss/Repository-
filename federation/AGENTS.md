# Federation Agent Instructions

- Do not invent provider claim names or endpoints.
- Treat issuer and audience as deployment data obtained from the actual provider configuration/token.
- Never log raw JWTs.
- Keep negative tests mandatory: wrong issuer, wrong audience, wrong instance, expired token, and missing required claim must fail closed.
- Do not automate changes to IAM or OpenAI trust configuration.
