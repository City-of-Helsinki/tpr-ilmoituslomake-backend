from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import SimpleTestCase
from django.urls import resolve
from helusers.jwt import JWT, ValidationError
from helusers.sessions import TunnistamoOIDCSerializer
from helusers.views import LoginView


class AuthenticationUpgradeTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.jwks = {
            "keys": [
                jwt.algorithms.RSAAlgorithm.to_jwk(
                    cls.private_key.public_key(), as_dict=True
                )
            ]
        }
        cls.token_settings = SimpleNamespace(
            ALLOWED_ALGORITHMS=["RS256"], ISSUER=["https://issuer.example.invalid"]
        )

    def make_token(self, **overrides):
        claims = {
            "sub": "test-user",
            "iss": "https://issuer.example.invalid",
            "aud": "test-api",
            "exp": 4102444800,
        }
        claims.update(overrides)
        return jwt.encode(claims, self.private_key, algorithm="RS256")

    def test_valid_rs256_token(self):
        token = JWT(self.make_token(), settings=self.token_settings)
        token.validate_issuer()
        token.validate(self.jwks, ["test-api"])

    def test_wrong_audience_is_rejected(self):
        token = JWT(self.make_token(aud="other-api"), settings=self.token_settings)
        with self.assertRaises(ValidationError):
            token.validate(self.jwks, ["test-api"])

    def test_wrong_issuer_is_rejected(self):
        token = JWT(
            self.make_token(iss="https://other.example.invalid"),
            settings=self.token_settings,
        )
        with self.assertRaises(ValidationError):
            token.validate_issuer()

    def test_expired_token_is_rejected(self):
        token = JWT(self.make_token(exp=1), settings=self.token_settings)
        with self.assertRaises(jwt.ExpiredSignatureError):
            token.validate(self.jwks, ["test-api"])

    def test_hmac_token_cannot_use_oidc_keys(self):
        encoded = jwt.encode(
            {"aud": "test-api", "exp": 4102444800}, "x" * 32, algorithm="HS256"
        )
        token = JWT(encoded, settings=self.token_settings)
        with self.assertRaises(jwt.InvalidAlgorithmError):
            token.validate(self.jwks, ["test-api"])

    def test_oidc_session_preserves_token_expiry_datetime(self):
        expiry = datetime(2026, 10, 27, 12, 0, tzinfo=timezone.utc)
        serializer = TunnistamoOIDCSerializer()
        session = serializer.loads(
            serializer.dumps({"access_token_expires_at": expiry})
        )
        self.assertEqual(session["access_token_expires_at"], expiry)

    def test_existing_get_login_redirect_is_preserved(self):
        self.assertIs(resolve("/helauth/login/").func.view_class, LoginView)
        with patch("helusers.views.logout"):
            response = self.client.get("/helauth/login/?next=/moderation/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/tunnistamo/", response["Location"])
        self.assertIn("next=%2Fmoderation%2F", response["Location"])
