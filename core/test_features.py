from django.test import TestCase
from django.urls import reverse
from .models import BrewMethod, CoffeeContent, ContentCategory

class PublishingTests(TestCase):
    def test_unpublished_content_hidden(self):
        method = BrewMethod.objects.create(name="طريقة مخفية", slug="hidden-method", short_description="س", description="و", difficulty="easy", duration_minutes=4, coffee_grams=20, water_ml=300, ratio="1:15", grind_size="متوسط", water_temperature=93)
        self.assertEqual(self.client.get(reverse("core:brew_detail", args=[method.slug])).status_code, 404)
        method.is_published=True; method.save(); self.assertEqual(self.client.get(reverse("core:brew_detail", args=[method.slug])).status_code, 200)
        category=ContentCategory.objects.create(name="أنواع البن",slug="beans",content_type="encyclopedia")
        article=CoffeeContent.objects.create(category=category,title="درس",slug="lesson",summary="ملخص",content="محتوى")
        self.assertEqual(self.client.get(reverse("core:knowledge_detail",args=[article.slug])).status_code,404)
