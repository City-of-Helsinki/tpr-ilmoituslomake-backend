from unittest.mock import patch

import jwt
from django.test import RequestFactory, SimpleTestCase

from moderation.views import image_proxy


class ImageProxyTokenTests(SimpleTestCase):
    secret = "image-proxy-regression-test-secret-at-least-32-bytes"

    def request_image(self, claims=None, secret=None):
        query = {}
        if claims is not None:
            query["token"] = jwt.encode(
                claims, secret or self.secret, algorithm="HS256"
            )
        request = RequestFactory().get("/api/proxy/441/image.jpg", query)
        with patch("moderation.views.JWT_IMAGE_SECRET", self.secret):
            return image_proxy(request, "441", "image.jpg")

    def test_valid_token_allows_matching_image(self):
        response = self.request_image(
            {"id": "441", "image": "image.jpg", "exp": 4102444800}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["X-Accel-Redirect"].startswith("/proxy/441/image.jpg"))

    def test_missing_token_is_rejected(self):
        self.assertEqual(self.request_image().status_code, 403)

    def test_expired_token_is_rejected(self):
        response = self.request_image({"id": "441", "image": "image.jpg", "exp": 1})
        self.assertEqual(response.status_code, 403)

    def test_wrong_signature_is_rejected(self):
        response = self.request_image(
            {"id": "441", "image": "image.jpg", "exp": 4102444800},
            secret="another-regression-test-secret-at-least-32-bytes",
        )
        self.assertEqual(response.status_code, 403)

    def test_token_cannot_access_another_image(self):
        response = self.request_image(
            {"id": "441", "image": "another.jpg", "exp": 4102444800}
        )
        self.assertEqual(response.status_code, 403)

    def test_token_cannot_access_another_notification(self):
        response = self.request_image(
            {"id": "442", "image": "image.jpg", "exp": 4102444800}
        )
        self.assertEqual(response.status_code, 403)
