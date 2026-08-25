import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from claims import FederationClaims
from validator import FederationPolicy, FederationRejected, authorize


BASE = {
    "iss": "oracle-issuer",
    "aud": ["openai-audience"],
    "exp": 2_000_000_000,
    "sub_type": "instance",
    "ipst_instance": "instance-a",
    "ipst_compartment": "compartment-a",
    "domain_id": "domain-a",
    "ca_ocid": "tenancy-a",
}
POLICY = FederationPolicy(
    issuer="oracle-issuer",
    audience="openai-audience",
    instance_id="instance-a",
    compartment_id="compartment-a",
    domain_id="domain-a",
    tenancy_id="tenancy-a",
)


def check(claims, now=1_900_000_000):
    authorize(FederationClaims.from_mapping(claims), POLICY, now=now)


def test_valid_identity_is_accepted():
    check(BASE)


@pytest.mark.parametrize("field,value", [
    ("iss", "wrong-issuer"),
    ("aud", ["wrong-audience"]),
    ("ipst_instance", "instance-b"),
    ("ipst_compartment", "compartment-b"),
    ("domain_id", "domain-b"),
    ("ca_ocid", "tenancy-b"),
    ("sub_type", "user"),
])
def test_wrong_identity_is_rejected(field, value):
    claims = BASE.copy()
    claims[field] = value
    with pytest.raises(FederationRejected):
        check(claims)


def test_expired_token_is_rejected():
    claims = BASE.copy()
    claims["exp"] = 1
    with pytest.raises(FederationRejected):
        check(claims)
