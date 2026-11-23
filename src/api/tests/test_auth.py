"""Tests for auth/jwt.py verify_token function."""
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException


def _make_test_rsa_key():
    """Generate a temporary RSA key pair for signing test JWTs."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_numbers = public_key.public_key_numbers()  # type: ignore[attr-defined]
    return private_key, private_pem, public_key, public_numbers


def _int_to_base64url(n: int) -> str:
    import base64

    length = (n.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()


def _make_jwks(public_key) -> dict:
    """Build a minimal JWKS from an RSA public key."""
    pub_numbers = public_key.public_key_numbers()  # type: ignore[attr-defined]
    return {
        "keys": [
            {
                "kty": "RSA",
                "use": "sig",
                "alg": "RS256",
                "kid": "test-key-1",
                "n": _int_to_base64url(pub_numbers.n),
                "e": _int_to_base64url(pub_numbers.e),
            }
        ]
    }


def _sign_jwt(private_pem: bytes, claims: dict) -> str:
    from jose import jwt

    return jwt.encode(claims, private_pem, algorithm="RS256", headers={"kid": "test-key-1"})


@pytest.fixture
def rsa_keypair():
    private_key, private_pem, public_key, _ = _make_test_rsa_key()
    return private_key, private_pem, public_key


@pytest.fixture
def jwks(rsa_keypair):
    _, _, public_key = rsa_keypair
    return _make_jwks(public_key)


def test_verify_token_valid(rsa_keypair, jwks):
    """verify_token with a valid JWT returns claims dict."""
    _, private_pem, _ = rsa_keypair

    claims_in = {
        "sub": "test-idp-001",
        "email": "test@example.com",
        "iss": "http://localhost:8080/local",
        "aud": "cigarlog",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
    }
    token = _sign_jwt(private_pem, claims_in)

    # Patch _get_jwks and settings
    with (
        patch("app.auth.jwt._get_jwks", return_value={"keys": jwks["keys"], "fetched_at": time.monotonic()}),
        patch("app.auth.jwt.settings") as mock_settings,
    ):
        mock_settings.OIDC_ISSUER = "http://localhost:8080/local"
        mock_settings.JWT_AUDIENCE = "cigarlog"

        from app.auth.jwt import verify_token

        result = verify_token(token)

    assert result["sub"] == "test-idp-001"
    assert result["email"] == "test@example.com"


def test_verify_token_expired(rsa_keypair, jwks):
    """verify_token with an expired JWT raises HTTPException 401."""
    _, private_pem, _ = rsa_keypair

    claims_in = {
        "sub": "test-idp-001",
        "email": "test@example.com",
        "iss": "http://localhost:8080/local",
        "aud": "cigarlog",
        "exp": int(time.time()) - 3600,  # expired
        "iat": int(time.time()) - 7200,
    }
    token = _sign_jwt(private_pem, claims_in)

    with (
        patch("app.auth.jwt._get_jwks", return_value={"keys": jwks["keys"], "fetched_at": time.monotonic()}),
        patch("app.auth.jwt.settings") as mock_settings,
    ):
        mock_settings.OIDC_ISSUER = "http://localhost:8080/local"
        mock_settings.JWT_AUDIENCE = "cigarlog"

        from app.auth.jwt import verify_token

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

    assert exc_info.value.status_code == 401


def test_verify_token_wrong_audience(rsa_keypair, jwks):
    """verify_token with wrong audience raises HTTPException 401."""
    _, private_pem, _ = rsa_keypair

    claims_in = {
        "sub": "test-idp-001",
        "email": "test@example.com",
        "iss": "http://localhost:8080/local",
        "aud": "wrong-audience",
        "exp": int(time.time()) + 3600,
        "iat": int(time.time()),
    }
    token = _sign_jwt(private_pem, claims_in)

    with (
        patch("app.auth.jwt._get_jwks", return_value={"keys": jwks["keys"], "fetched_at": time.monotonic()}),
        patch("app.auth.jwt.settings") as mock_settings,
    ):
        mock_settings.OIDC_ISSUER = "http://localhost:8080/local"
        mock_settings.JWT_AUDIENCE = "cigarlog"

        from app.auth.jwt import verify_token

        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

    assert exc_info.value.status_code == 401
