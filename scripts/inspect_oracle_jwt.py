#!/usr/bin/env python3
"""Inspect JWT structure/payload without performing signature verification.

Usage:
  printf '%s' "$TOKEN" | python scripts/inspect_oracle_jwt.py

The token is read from stdin and is never echoed. This tool is diagnostic only;
its output is not evidence that the token is authentic or trusted.
"""

from __future__ import annotations

import base64
import json
import sys
from typing import Any

EXPECTED = (
    "iss",
    "aud",
    "sub_type",
    "ipst_instance",
    "ipst_compartment",
    "domain_id",
    "ca_ocid",
    "exp",
)


def decode_part(value: str) -> Any:
    padded = value + "=" * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))


def inspect_token(token: str) -> None:
    """Print only safe structural metadata for a token held in memory."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Input is not a compact JWT")

    header = decode_part(parts[0])
    payload = decode_part(parts[1])
    if not isinstance(header, dict) or not isinstance(payload, dict):
        raise ValueError("JWT header/payload are not JSON objects")

    print("JWT structural decode: OK")
    print("Signature verification: NOT PERFORMED")
    print("Header fields:", ", ".join(sorted(header)))
    print("Payload claim inventory:")
    for claim in EXPECTED:
        if claim in payload:
            print(f"  {claim}: present ({type(payload[claim]).__name__})")
        else:
            print(f"  {claim}: MISSING")

    if isinstance(payload.get("aud"), list):
        print("  aud cardinality:", len(payload["aud"]))
    elif "aud" in payload:
        print("  aud cardinality: 1")

    print("Token value: NOT PRINTED")


def main() -> int:
    token = sys.stdin.read().strip()
    if not token:
        raise SystemExit("No token supplied on stdin")
    inspect_token(token)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"JWT inspection failed: {type(exc).__name__}", file=sys.stderr)
        raise SystemExit(1)
