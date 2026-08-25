"""Provider-neutral claim representation for federation tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class FederationClaims:
    issuer: str
    audience: tuple[str, ...]
    expires_at: int
    subject_type: str | None = None
    instance_id: str | None = None
    compartment_id: str | None = None
    domain_id: str | None = None
    tenancy_id: str | None = None

    @classmethod
    def from_mapping(cls, claims: Mapping[str, Any]) -> "FederationClaims":
        audience = claims.get("aud")
        if isinstance(audience, str):
            normalized = (audience,)
        elif isinstance(audience, list) and all(isinstance(x, str) for x in audience):
            normalized = tuple(audience)
        else:
            raise ValueError("aud must be a string or list of strings")

        issuer = claims.get("iss")
        exp = claims.get("exp")
        if not isinstance(issuer, str) or not issuer:
            raise ValueError("iss is required")
        if not isinstance(exp, (int, float)):
            raise ValueError("exp is required and must be numeric")

        return cls(
            issuer=issuer,
            audience=normalized,
            expires_at=int(exp),
            subject_type=claims.get("sub_type"),
            instance_id=claims.get("ipst_instance"),
            compartment_id=claims.get("ipst_compartment"),
            domain_id=claims.get("domain_id"),
            tenancy_id=claims.get("ca_ocid"),
        )
