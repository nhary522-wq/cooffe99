from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from payments.models import Payment

from .models import Order, Shipment


class StoreOrderFlowTests(TestCase):
    def setUp(self):
        self.slug = "coffee-grinders"

    def add_product(self, slug=None, quantity=1):
        return self.client.post(
            reverse("orders:add_to_cart", args=[slug or self.slug]),
            {"quantity": quantity, "next": reverse("orders:cart")},
        )

    def checkout_data(self, **overrides):
        data = {
            "first_name": "عميل",
            "last_name": "الاختبار",
            "email": "customer@example.com",
            "phone": "0556229463",
            "city": "الرياض",
            "district": "الياسمين",
            "street": "شارع القهوة",
            "building_number": "23",
            "postal_code": "12345",
            "payment_method": "cash_on_delivery",
            "notes": "اتصل قبل التوصيل",
        }
        data.update(overrides)
        return data

    def test_add_update_remove_and_csrf_protection(self):
        self.assertRedirects(self.add_product(), reverse("orders:cart"))
        cart = self.client.get(reverse("orders:cart"))
        self.assertContains(cart, "مطاحن القهوة")
        self.assertContains(cart, "249")

        self.client.post(reverse("orders:update_cart", args=[self.slug]), {"quantity": 2})
        self.assertEqual(self.client.session["cart"][self.slug], 2)
        self.client.post(reverse("orders:remove_from_cart", args=[self.slug]))
        self.assertNotIn(self.slug, self.client.session["cart"])

        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(reverse("orders:add_to_cart", args=[self.slug]))
        self.assertEqual(response.status_code, 403)

    def test_checkout_creates_order_payment_and_shipment(self):
        self.add_product()
        response = self.client.post(reverse("orders:checkout"), self.checkout_data())
        order = Order.objects.get()
        self.assertRedirects(
            response,
            reverse("orders:order_detail", args=[order.order_number]),
        )
        self.assertEqual(order.status, "confirmed")
        self.assertEqual(order.customer_email, "customer@example.com")
        self.assertEqual(order.shipping_amount, Decimal("20.00"))
        self.assertEqual(order.total_amount, Decimal("269.00"))
        self.assertEqual(order.items.count(), 1)
        self.assertTrue(Payment.objects.filter(order=order, status="pending").exists())
        self.assertTrue(Shipment.objects.filter(order=order, status="pending").exists())
        self.assertEqual(self.client.session["cart"], {})
        self.assertContains(self.client.get(response.url), order.order_number)

    def test_fixed_shipping_and_electronic_payment_pending(self):
        self.add_product(slug="espresso-cups")
        cart = self.client.get(reverse("orders:cart"))
        self.assertContains(cart, "20")
        response = self.client.post(
            reverse("orders:checkout"),
            self.checkout_data(payment_method="mada"),
        )
        order = Order.objects.get()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.shipping_amount, Decimal("20.00"))

    def test_order_detail_is_private_to_owner_or_checkout_session(self):
        order = Order.objects.create(
            customer_name="غير مصرح",
            customer_email="private@example.com",
            customer_phone="966500000000",
            shipping_city="الرياض",
            shipping_district="حي",
            shipping_street="شارع",
        )
        self.assertEqual(
            self.client.get(
                reverse("orders:order_detail", args=[order.order_number])
            ).status_code,
            404,
        )
