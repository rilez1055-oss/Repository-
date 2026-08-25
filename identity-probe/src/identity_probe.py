"""OCI workload identity probe.

This module deliberately keeps provider-specific token acquisition separate from
claim validation. The validation functions accept decoded claims so they can be
tested without contacting OCI.
"""

from __future__ import annotations

import time
from collections.abc import Mapping


class IdentityValidationError(ValueError):
    """Raised when required workload identity evidence is missing or invalid."""


def validate_claims(
    claims: Mapping[str, object],
    *,
    expected_issuer: str | None = None,
    expected_audience: str | None = None,
    expected_instance: str | None = None,
    now: int | None = None,
) -> None:
    """Validate the minimum evidence required by the reference gate.

    This is not a JWT signature verifier. Signature and issuer verification must
    happen in the component that obtains/verifies the provider token. This
    function validates the resulting claims against deployment policy.
    """
    required = ("iss", "aud", "exp")
    missing = [name for name in required if not claims.get(name)]
    if missing:
        raise IdentityValidationError(f"missing required claims: {', '.join(missing)}")

    if expected_issuer is not None and claims["iss"] != expected_issuer:
        raise IdentityValidationError("issuer mismatch")

    audience = claims["aud"]
    audiences = audience if isinstance(audience, list) else [audience]
    if expected_audience is not None and expected_audience not in audiences:
        raise IdentityValidationError("audience mismatch")

    if expected_instance is not None and claims.get("ipst_instance") != expected_instance:
        raise IdentityValidationError("instance identity mismatch")

    exp = claims["exp"]
    if not isinstance(exp, (int, float)):
        raise IdentityValidationError("exp must be numeric")
    if exp <= (time.time() if now is None else now):
        raise IdentityValidationError("token is expired")


def redact_identifier(value: str, visible: int = 4) -> str:
    """Redact an identifier for logs while retaining a small diagnostic suffix."""
    if len(value) <= visible:
        return "<redacted>"
    return f"<redacted>…{value[-visible:]}"
