from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from accounts.models import Address, LoyaltyTransaction
from .models import Order
from .subscription_models import Subscription, SubscriptionPlan
from .subscription_services import create_due_box

class SubscriptionAndLoyaltyTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user("subscriber",password="pass12345"); self.address=Address.objects.create(user=self.user,recipient_name="مستخدم",phone="0500000000",city="الرياض",district="حي",street="شارع")
        self.plan=SubscriptionPlan.objects.create(name="صندوق",slug="box",description="x",price=99,interval_days=30)
    def test_no_duplicate_box(self):
        sub=Subscription.objects.create(user=self.user,plan=self.plan,address=self.address,start_date=date.today(),next_shipment_at=timezone.now()-timedelta(days=1),status="active")
        first=create_due_box(sub.pk); sub.next_shipment_at=timezone.now()-timedelta(days=1); sub.save(); second=create_due_box(sub.pk); self.assertEqual(first.pk,second.pk); self.assertEqual(sub.boxes.count(),1)
    def test_loyalty_awarded_once_and_reversed(self):
        order=Order.objects.create(user=self.user,status="delivered",customer_name="x",customer_email="x@x.com",customer_phone="1",shipping_city="x",shipping_district="x",shipping_street="x",total_amount=100)
        order.save(); self.assertEqual(LoyaltyTransaction.objects.filter(order=order,transaction_type="earn").count(),1)
        order.status="cancelled"; order.save(); self.assertEqual(LoyaltyTransaction.objects.filter(order=order,transaction_type="reverse").count(),1)
