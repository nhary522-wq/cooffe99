from django.test import TestCase
from django.urls import reverse


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
