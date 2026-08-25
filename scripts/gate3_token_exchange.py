#!/usr/bin/env python3
"""Gate 3: OCI Instance Principal -> Oracle Identity Domain token.

Run only inside the OCI workload. Never logs the token or auth material.
"""

import os
import sys

import oci
import requests


def main() -> int:
    domain = os.environ["OCI_IDENTITY_DOMAIN_URL"].rstrip("/")

    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    response = requests.post(
        f"{domain}/oauth2/v1/token",
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "scope": "urn:opc:idm:__myscopes__",
            "requested_token_type":
                "urn:opc:params:oauth:token-type:access_token",
        },
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded;charset=utf-8",
        },
        auth=signer,
        timeout=30,
    )
    response.raise_for_status()

    token = response.json().get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("No Oracle access token returned")

    print("Oracle token acquired: YES")
    print("Token length:", len(token))
    print("Token persisted: NO")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Preserve useful exception classification while avoiding response bodies,
        # headers, tokens, and signer material.
        print(f"Gate 3 failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
