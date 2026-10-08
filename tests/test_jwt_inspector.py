import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from inspect_oracle_jwt import inspect_token  # noqa: E402


def compact_jwt(payload):
    def enc(value):
        raw = json.dumps(value, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    return f"{enc({'alg': 'RS256', 'typ': 'JWT'})}.{enc(payload)}.signature"


def test_inspector_decodes_without_printing_token(capsys):
    token = compact_jwt({"iss": "issuer", "aud": ["a", "b"], "exp": 123})
    inspect_token(token)
    output = capsys.readouterr().out

    assert "JWT structural decode: OK" in output
    assert "Signature verification: NOT PERFORMED" in output
    assert "aud cardinality: 2" in output
    assert token not in output
    assert "Token value: NOT PRINTED" in output
