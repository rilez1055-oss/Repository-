"""Fail-closed federation policy checks."""

from __future__ import annotations

import time
from dataclasses import dataclass

from claims import FederationClaims


class FederationRejected(ValueError):
    """Raised when a workload does not satisfy federation policy."""


@dataclass(frozen=True)
class FederationPolicy:
    issuer: str
    audience: str
    subject_type: str = "instance"
    instance_id: str | None = None
    compartment_id: str | None = None
    domain_id: str | None = None
    tenancy_id: str | None = None


def authorize(claims: FederationClaims, policy: FederationPolicy, *, now: int | None = None) -> None:
    current = int(time.time()) if now is None else now
    if claims.issuer != policy.issuer:
        raise FederationRejected("issuer mismatch")
    if policy.audience not in claims.audience:
        raise FederationRejected("audience mismatch")
    if claims.expires_at <= current:
        raise FederationRejected("token expired")
    if policy.subject_type and claims.subject_type != policy.subject_type:
        raise FederationRejected("subject type mismatch")
    if policy.instance_id is not None and claims.instance_id != policy.instance_id:
        raise FederationRejected("instance mismatch")
    if policy.compartment_id is not None and claims.compartment_id != policy.compartment_id:
        raise FederationRejected("compartment mismatch")
    if policy.domain_id is not None and claims.domain_id != policy.domain_id:
        raise FederationRejected("domain mismatch")
    if policy.tenancy_id is not None and claims.tenancy_id != policy.tenancy_id:
        raise FederationRejected("tenancy mismatch")
