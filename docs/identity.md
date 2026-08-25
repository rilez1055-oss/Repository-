# OCI identity gates

## Verified provider behavior

The current OpenAI OCI workload-identity guide documents this flow:

1. OCI Compute instance principal reaches the IMDSv2 endpoint.
2. `oci.auth.signers.InstancePrincipalsSecurityTokenSigner` signs an OAuth token-exchange request to the Oracle identity domain.
3. The identity domain returns a short-lived IDCS access token.
4. The token is inspected locally as a JWT payload; raw tokens are treated as secrets and are not logged or sent to third-party decoders.
5. OpenAI uses the Oracle token as the subject token for workload identity federation.

OpenAI explicitly says to use the actual Oracle token's `iss` and an actual `aud` value rather than assuming an OpenAI audience. The documented claims include `sub_type`, `ipst_instance`, `ipst_compartment`, `domain_id`, and `ca_ocid`.

## Gate 1 — OCI identity acquisition

Run from an OCI Compute instance configured for Instance Principals:

```bash
export OCI_IDENTITY_DOMAIN_URL="https://<your-identity-domain>"
python identity-probe/src/run_probe.py
```

Gate 1 requires:

- IMDSv2 reachable with `Authorization: Bearer Oracle`.
- Instance ID, compartment ID, and region available.
- Instance-principal signer can initialize.
- Oracle identity-domain token exchange succeeds.
- Returned credential is a compact JWT.

## Gate 2 — local claim inspection

The probe validates:

- `iss` exists.
- `aud` exists.
- `exp` is numeric and in the future.
- `sub_type == "instance"`.
- `ipst_instance` equals the instance metadata ID.
- `ipst_compartment` equals the instance metadata compartment.

The probe does **not** claim to verify the JWT signature. Signature verification is performed by the relying party during federation. The local decoder is evidence collection and policy validation, not an issuer-verification mechanism.

## What the probe never does

- prints the raw Oracle token;
- persists the Oracle token;
- sends the token to a JWT decoder service;
- guesses the issuer or audience;
- silently falls back to an API key;
- treats a successful metadata HTTP response as sufficient proof of identity.

## OKE caveat

The standard OCI instance-principal signer may identify the worker node rather than an individual OKE pod. Do not interpret an instance-level mapping as pod-level isolation without verifying the workload identity mechanism actually used by the pod.
