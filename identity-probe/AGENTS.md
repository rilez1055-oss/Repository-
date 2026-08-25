# Identity Probe Agent Instructions

- Never print or persist Oracle access tokens.
- Redact OCIDs in ordinary logs.
- Do not modify OCI IAM configuration.
- Fail closed when required identity evidence is absent.
- Separate connectivity checks from identity validation.
- Unit tests must cover missing, malformed, and expired identity data.
