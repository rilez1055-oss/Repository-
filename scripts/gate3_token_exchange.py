#!/usr/bin/env python3
"""Gate 3: OCI Instance Principal -> Oracle Identity Domain access token.

Run only inside the OCI workload. The token is process-local and is never
printed, persisted, or included in exception text.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any

import oci
import requests


TOKEN_EXCHANGE_GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN_TYPE = "urn:opc:params:oauth:token-type:access_token"
DEFAULT_SCOPE = "urn:opc:idm:__myscopes__"


def exchange_token() -> str:
    """Perform the Gate 3 exchange and return the token only in process memory."""
    domain = os.environ.get("OCI_IDENTITY_DOMAIN_URL", "").strip().rstrip("/")
    if not domain:
        raise ValueError("OCI_IDENTITY_DOMAIN_URL is required")
    if not domain.startswith("https://"):
        raise ValueError("OCI_IDENTITY_DOMAIN_URL must use https://")

    scope = os.environ.get("OCI_IDENTITY_DOMAIN_SCOPE", DEFAULT_SCOPE).strip()
    if not scope:
        raise ValueError("OCI_IDENTITY_DOMAIN_SCOPE must not be empty")

    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    response = requests.post(
        f"{domain}/oauth2/v1/token",
        data={
            "grant_type": TOKEN_EXCHANGE_GRANT,
            "scope": scope,
            "requested_token_type": ACCESS_TOKEN_TYPE,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        },
        auth=signer,
        timeout=30,
    )
    response.raise_for_status()

    payload: Any = response.json()
    token = payload.get("access_token") if isinstance(payload, dict) else None
    if not isinstance(token, str) or not token:
        raise RuntimeError("Token exchange response did not contain access_token")
    return token


def _safe_error(exc: Exception) -> str:
    """Return classification only; never serialize exception details."""
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        return f"{type(exc).__name__} (HTTP {exc.response.status_code})"
    return type(exc).__name__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inspect-claims",
        action="store_true",
        help="Decode safe JWT structure/claim inventory in-process; never print token.",
    )
    args = parser.parse_args()

    token = exchange_token()
    print("Oracle token acquired: YES")
    print("Token length:", len(token))
    print("Token persisted: NO")

    if args.inspect_claims:
        from inspect_oracle_jwt import inspect_token

        inspect_token(token)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Gate 3 failed: {_safe_error(exc)}", file=sys.stderr)
        raise SystemExit(1)
