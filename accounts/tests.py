import os
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class AccountFlowTests(TestCase):
    def setUp(self):
        self.password = "StrongPass!482"

    def test_register_creates_profile_and_logs_user_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "first_name": "محمد",
                "last_name": "علي",
                "email": "customer@example.com",
                "phone": "0501234567",
                "password": self.password,
                "password_confirm": self.password,
            },
            follow=True,
        )

        user = get_user_model().objects.get(email="customer@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Profile.objects.get(user=user).phone, "966501234567")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_login_accepts_email_and_phone(self):
        user = get_user_model().objects.create_user(
            username="customer",
            email="login@example.com",
            password=self.password,
        )
        Profile.objects.create(user=user, phone="966501112233")

        for identifier in ("login@example.com", "0501112233"):
            self.client.post(reverse("accounts:logout"))
            response = self.client.post(
                reverse("accounts:login"),
                {"identifier": identifier, "password": self.password},
            )
            self.assertRedirects(response, reverse("core:home"))
            self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_social_buttons_and_unconfigured_routes_are_safe(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, reverse("accounts:social_login", args=["google"]))
        self.assertContains(response, reverse("accounts:social_login", args=["apple"]))

        for provider in ("google", "apple"):
            response = self.client.get(
                reverse("accounts:social_login", args=[provider]),
            )
            self.assertRedirects(response, reverse("accounts:login"))

    def test_configured_social_routes_start_oauth(self):
        provider_settings = {
            "google": {
                "APP": {
                    "client_id": "google-client",
                    "secret": "google-secret",
                    "key": "",
                },
                "SCOPE": ["profile", "email"],
            },
            "apple": {
                "APP": {
                    "client_id": "apple-client",
                    "secret": "apple-secret",
                    "key": "apple-key",
                    "settings": {"certificate_key": "test-key"},
                },
            },
        }
        environment = {
            "GOOGLE_CLIENT_ID": "google-client",
            "APPLE_CLIENT_ID": "apple-client",
        }
        with (
            mock.patch.dict(os.environ, environment),
            self.settings(SOCIALACCOUNT_PROVIDERS=provider_settings),
        ):
            google = self.client.get(
                reverse("accounts:social_login", args=["google"]),
                follow=True,
            )
            apple = self.client.get(
                reverse("accounts:social_login", args=["apple"]),
                follow=True,
            )

        self.assertIn("accounts.google.com", google.redirect_chain[-1][0])
        self.assertIn("appleid.apple.com", apple.redirect_chain[-1][0])
