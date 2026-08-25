# Agent / Repository Policy

## Security invariants

1. Do not mark a security gate PASS because implementation exists. Record runtime evidence.
2. Never log or persist JWTs, bearer tokens, authorization headers, cookies, private keys, signer material, or raw customer/resource authorization context.
3. Prompt cache state is an optimization only. It never establishes identity or authorization.
4. Privileged operations must authorize `principal + action + resource + current policy` at the authoritative execution boundary.
5. Skills are privileged code/instructions. Inspect, approve, version-pin, and constrain them before execution.
6. Do not expose an arbitrary open Skill catalog to end users.
7. High-impact or write actions require explicit approval/policy enforcement.
8. Keep dynamic authorization context, current resources, timestamps, transient tool results, and user input out of stable cacheable prefixes when practical.
9. Do not implement OpenAI WIF or claim a working OpenAI SDK constructor from an unverified example. Re-check the current API documentation when Gate 4/6 opens.
10. Do not use model choice as evidence for identity, federation, or authorization.

## Gate 3 rule

Gate 3 is active until the OCI workload produces the three-line non-secret evidence:

```text
Oracle token acquired: YES
Token length: <number>
Token persisted: NO
```

A later OpenAI rejection does not retroactively fail Gate 3; it belongs to Gate 4 or a downstream gate.
