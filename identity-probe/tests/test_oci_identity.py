import json

import pytest

from oci_identity import (
    ProbeError,
    decode_jwt_payload,
    get_instance_metadata,
)


def test_decode_jwt_payload_without_logging_or_verification():
    import base64

    payload = {"iss": "https://identity.oraclecloud.com/", "exp": 2000}
    encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
    token = f"header.{encoded}.signature"

    assert decode_jwt_payload(token) == payload


def test_decode_rejects_non_jwt():
    with pytest.raises(ProbeError, match="not a compact JWT"):
        decode_jwt_payload("not-a-jwt")


def test_metadata_uses_imdsv2(monkeypatch):
    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "id": "ocid1.instance.example",
                "compartmentId": "ocid1.compartment.example",
                "region": "us-test-1",
            }

    captured = {}

    def fake_get(url, **kwargs):
        captured.update(url=url, kwargs=kwargs)
        return Response()

    monkeypatch.setattr("oci_identity.requests.get", fake_get)
    result = get_instance_metadata()

    assert result.instance_id == "ocid1.instance.example"
    assert captured["url"].endswith("/opc/v2/instance/")
    assert captured["kwargs"]["headers"] == {"Authorization": "Bearer Oracle"}


def test_metadata_failure_is_fail_closed(monkeypatch):
    def fake_get(*args, **kwargs):
        raise RuntimeError("unexpected")

    monkeypatch.setattr("oci_identity.requests.get", fake_get)

    with pytest.raises(RuntimeError):
        get_instance_metadata()
