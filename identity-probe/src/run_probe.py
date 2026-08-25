"""Command-line entry point for the live OCI identity gates."""

from __future__ import annotations

import argparse
import json
import os

from identity_probe import redact_identifier
from oci_identity import ProbeError, run_probe


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OCI identity Gate 1 and Gate 2")
    parser.add_argument(
        "--identity-domain-url",
        default=os.environ.get("OCI_IDENTITY_DOMAIN_URL"),
        help="Oracle Identity Domain base URL (or OCI_IDENTITY_DOMAIN_URL)",
    )
    args = parser.parse_args()

    if not args.identity_domain_url:
        parser.error("--identity-domain-url or OCI_IDENTITY_DOMAIN_URL is required")

    try:
        result = run_probe(args.identity_domain_url)
    except ProbeError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}))
        return 1

    claims = result.claims
    safe_claims = {
        "iss": claims.get("iss"),
        "aud": claims.get("aud"),
        "sub_type": claims.get("sub_type"),
        "ipst_instance": redact_identifier(str(claims["ipst_instance"])),
        "ipst_compartment": redact_identifier(str(claims["ipst_compartment"])),
        "domain_id": redact_identifier(str(claims["domain_id"])),
        "ca_ocid": redact_identifier(str(claims["ca_ocid"])),
        "exp": claims.get("exp"),
        "iat": claims.get("iat"),
    }

    print(
        json.dumps(
            {
                "status": "PASS",
                "gate_1": "PASS",
                "gate_2": "PASS",
                "instance": redact_identifier(result.metadata.instance_id),
                "region": result.metadata.region,
                "claims": safe_claims,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
