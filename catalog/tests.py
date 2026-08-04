from django.test import TestCase
from django.urls import reverse

from .services import get_store_items


class CatalogTests(TestCase):
    def test_catalog_sections_and_product_detail(self):
        landing = self.client.get(reverse("catalog:product_list"))
        self.assertContains(landing, "محاصيل القهوة")
        self.assertContains(landing, "أدوات القهوة")

        crops = self.client.get(reverse("catalog:crops"))
        self.assertContains(crops, "شلشلي إثيوبي")
        self.assertNotContains(crops, "مطحنة يدوية")

        detail = self.client.get(
            reverse("catalog:product_detail", args=["shalshali-ethiopian"])
        )
        self.assertContains(detail, "عرض المنتج")
        self.assertContains(detail, "إضافة إلى السلة")

    def test_catalog_search(self):
        response = self.client.get(reverse("catalog:product_list"), {"q": "مطحنة"})
        self.assertContains(response, "مطحنة يدوية")
        self.assertNotContains(response, "بلقيس اليمن")

    def test_crop_and_tool_images_match_requested_catalog_style(self):
        crops = get_store_items("crops")
        tools = get_store_items("tools")
        self.assertEqual(len({item["image"] for item in crops}), 1)
        self.assertIn("photo-1559056199-641a0ac8b55e", crops[0]["image"])
        self.assertEqual(len({item["image"] for item in tools}), len(tools))
        for item in tools:
            self.assertTrue(item["image"].startswith("/static/images/tools/"))
