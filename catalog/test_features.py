from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Category, Product, ProductReview

class ProductFeatureTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="محاصيل", slug="crops")
        self.product = Product.objects.create(category=self.category, name="محصول اختبار", slug="crop-test", sku="CROP-1", description="وصف", price=50, stock=3, country="إثيوبيا", flavor_notes="fruity")
    def test_product_detail_and_hidden_product(self):
        self.assertContains(self.client.get(reverse("catalog:product_detail", args=[self.product.slug])), "إثيوبيا")
        self.product.is_published = False; self.product.save(); self.assertEqual(self.client.get(reverse("catalog:product_detail", args=[self.product.slug])).status_code, 404)
    def test_compare_limits_and_duplicates(self):
        for i in range(5):
            p = Product.objects.create(category=self.category, name=f"P{i}", slug=f"p{i}", sku=f"P{i}", description="x", price=10, stock=1)
            self.client.post(reverse("catalog:compare_add", args=[p.pk]))
        self.assertEqual(len(self.client.session["compare_products"]), 4)
    def test_review_requires_login_and_verified_is_server_controlled(self):
        url = reverse("catalog:save_review", args=[self.product.slug]); self.assertEqual(self.client.post(url).status_code, 302)
        user = get_user_model().objects.create_user("reviewer", password="pass12345"); self.client.force_login(user)
        self.client.post(url, {"rating":5,"quality_rating":5,"aroma_rating":5,"sweetness_rating":5,"acidity_rating":4,"body_rating":4,"value_rating":5,"title":"جيد","comment":"ممتاز"})
        review = ProductReview.objects.get(); self.assertFalse(review.is_verified_purchase); self.assertFalse(review.is_approved)
