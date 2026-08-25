"""OCI Instance Principal -> Oracle Identity Domain probe.

The probe is intentionally diagnostic only. It acquires a short-lived Oracle
Identity Domain access token using the OCI Instance Principals signer, decodes
its JWT payload locally, and validates deployment claims. It never prints or
persists the token.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

import oci
import requests

from identity_probe import IdentityValidationError, validate_claims

IMDS_BASE_URL = "http://169.254.169.254/opc/v2"
IMDS_HEADERS = {"Authorization": "Bearer Oracle"}
TOKEN_EXCHANGE_GRANT = "urn:ietf:params:oauth:grant-type:token-exchange"
ACCESS_TOKEN_TYPE = "urn:opc:idm:__myscopes__"
REQUESTED_ACCESS_TOKEN_TYPE = "urn:opc:idm:__myscopes__"


class ProbeError(RuntimeError):
    """Raised when a live OCI identity gate cannot be completed."""


@dataclass(frozen=True)
class InstanceMetadata:
    instance_id: str
    compartment_id: str
    region: str


@dataclass(frozen=True)
class ProbeResult:
    metadata: InstanceMetadata
    claims: dict[str, Any]


def get_instance_metadata(*, timeout: float = 5.0) -> InstanceMetadata:
    """Read the minimum instance metadata required by Gate 1 using IMDSv2."""
    try:
        response = requests.get(
            f"{IMDS_BASE_URL}/instance/",
            headers=IMDS_HEADERS,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ProbeError(f"OCI instance metadata unavailable: {exc}") from exc

    required = ("id", "compartmentId", "region")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ProbeError(f"OCI instance metadata missing: {', '.join(missing)}")

    return InstanceMetadata(
        instance_id=str(payload["id"]),
        compartment_id=str(payload["compartmentId"]),
        region=str(payload["region"]),
    )


def acquire_identity_domain_token(identity_domain_url: str, *, timeout: float = 30.0) -> str:
    """Exchange the OCI instance principal for an IDCS access token."""
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
    response = requests.post(
        f"{identity_domain_url.rstrip('/')}/oauth2/v1/token",
        data={
            "grant_type": TOKEN_EXCHANGE_GRANT,
            "scope": ACCESS_TOKEN_TYPE,
            "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        auth=signer,
        timeout=timeout,
    )
    try:
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise ProbeError(f"Oracle identity-domain token exchange failed: {exc}") from exc

    token = payload.get("access_token")
    if not isinstance(token, str) or not token:
        raise ProbeError("Oracle identity-domain response did not contain an access_token")
    return token


def decode_jwt_payload(token: str) -> dict[str, Any]:
    """Decode a JWT payload without verifying its signature.

    This is diagnostic parsing only. Signature verification is deliberately not
    implemented here because OpenAI is the relying party that verifies the
    external subject token during workload-identity federation.
    """
    parts = token.split(".")
    if len(parts) != 3:
        raise ProbeError("identity token is not a compact JWT")

    try:
        payload = base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4))
        claims = json.loads(payload)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ProbeError("identity token payload is not valid JSON") from exc

    if not isinstance(claims, dict):
        raise ProbeError("identity token payload must be a JSON object")
    return claims


def run_probe(identity_domain_url: str) -> ProbeResult:
    """Run Gate 1 + Gate 2 against the current OCI instance."""
    metadata = get_instance_metadata()
    token = acquire_identity_domain_token(identity_domain_url)
    claims = decode_jwt_payload(token)

    try:
        validate_claims(
            claims,
            expected_instance=metadata.instance_id,
        )
    except IdentityValidationError as exc:
        raise ProbeError(f"identity claim validation failed: {exc}") from exc

    expected_compartment = metadata.compartment_id
    if claims.get("ipst_compartment") != expected_compartment:
        raise ProbeError("token compartment does not match instance metadata")

    if claims.get("sub_type") != "instance":
        raise ProbeError("token sub_type is not 'instance'")

    return ProbeResult(metadata=metadata, claims=claims)
