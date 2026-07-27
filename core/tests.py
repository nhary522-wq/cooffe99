from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_auth_buttons_and_requested_crops_are_visible(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:register"))
        self.assertContains(response, reverse("accounts:login"))
        self.assertContains(response, 'href="#crop-collection"')
        for crop in (
            "شلشلي إثيوبي",
            "مزيج البهاء",
            "بلقيس اليمن",
            "روبي كلومبي",
        ):
            self.assertContains(response, crop)
