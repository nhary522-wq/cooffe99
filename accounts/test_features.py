from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .models import CoffeeJournalEntry, LoyaltyAccount, LoyaltyTransaction

class AccountFeatureTests(TestCase):
    def setUp(self): self.u1=get_user_model().objects.create_user("u1",password="pass12345"); self.u2=get_user_model().objects.create_user("u2",password="pass12345")
    def test_journal_ownership(self):
        entry=CoffeeJournalEntry.objects.create(user=self.u2,external_product_name="خارجي",experienced_at=timezone.now(),overall_rating=4)
        self.client.force_login(self.u1); self.assertEqual(self.client.get(reverse("accounts:journal_detail",args=[entry.pk])).status_code,404)
    def test_loyalty_page_login_required(self): self.assertEqual(self.client.get(reverse("accounts:loyalty")).status_code,302)
