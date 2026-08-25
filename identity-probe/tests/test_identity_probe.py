import pytest

from identity_probe import IdentityValidationError, redact_identifier, validate_claims


BASE = {
    "iss": "https://identity.example",
    "aud": ["openai-example"],
    "exp": 2_000_000_000,
    "ipst_instance": "instance-123",
}


def test_valid_claims_pass():
    validate_claims(
        BASE,
        expected_issuer="https://identity.example",
        expected_audience="openai-example",
        expected_instance="instance-123",
        now=1_900_000_000,
    )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda c: c.update(iss="wrong"),
        lambda c: c.update(aud=["wrong"]),
        lambda c: c.update(ipst_instance="other"),
        lambda c: c.update(exp=1),
        lambda c: c.pop("aud"),
    ],
)
def test_invalid_claims_rejected(mutator):
    claims = BASE.copy()
    mutator(claims)
    with pytest.raises(IdentityValidationError):
        validate_claims(
            claims,
            expected_issuer="https://identity.example",
            expected_audience="openai-example",
            expected_instance="instance-123",
            now=1_900_000_000,
        )


def test_redaction():
    assert redact_identifier("ocid1.instance.example123") == "<redacted>…ple123"
