from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class DashboardPermissionTests(TestCase):
    def test_staff_only(self):
        user=get_user_model().objects.create_user("normal",password="pass12345"); self.client.force_login(user); self.assertEqual(self.client.get(reverse("dashboard:analytics")).status_code,302)
        user.is_staff=True; user.save(); self.assertEqual(self.client.get(reverse("dashboard:analytics")).status_code,200)
