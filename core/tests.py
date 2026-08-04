import json
from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from orders.models import Order


class HomePageTests(TestCase):
    def test_auth_buttons_and_catalog_links_are_visible(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("accounts:register"))
        self.assertContains(response, reverse("accounts:login"))
        self.assertContains(response, reverse("catalog:product_list"))
        self.assertContains(response, reverse("catalog:crops"))
        self.assertContains(response, reverse("catalog:tools"))
        self.assertContains(response, reverse("orders:cart"))

    def test_hero_uses_local_autoplay_video(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, 'class="coffee-hero-video"')
        self.assertContains(response, "autoplay")
        self.assertContains(response, "muted")
        self.assertContains(response, "loop")
        self.assertContains(response, "playsinline")
        self.assertContains(
            response,
            "/media/cooffe%20Video.%20png.mp4",
        )

    def test_customer_service_pages_and_contact_details(self):
        routes = (
            "core:contact",
            "core:faq",
            "core:shipping_policy",
            "core:return_policy",
            "core:track_order",
        )
        for route in routes:
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200)

        contact = self.client.get(reverse("core:contact"))
        self.assertContains(contact, "0556229463")
        self.assertContains(contact, "tel:+966556229463")
        self.assertContains(contact, "nhary522@gmail.com")
        self.assertContains(contact, "mailto:nhary522@gmail.com")

        home = self.client.get(reverse("core:home"))
        for route in routes:
            self.assertContains(home, reverse(route))

    def test_order_tracking_requires_matching_phone(self):
        order = Order.objects.create(
            customer_name="عميل الاختبار",
            customer_email="customer@example.com",
            customer_phone="0556229463",
            shipping_city="الرياض",
            shipping_district="الياسمين",
            shipping_street="شارع الاختبار",
            total_amount="120.00",
            status="shipped",
        )

        valid_response = self.client.post(
            reverse("core:track_order"),
            {
                "order_number": order.order_number,
                "phone": "0556229463",
            },
        )
        self.assertContains(valid_response, order.order_number)
        self.assertContains(valid_response, order.get_status_display())

        invalid_response = self.client.post(
            reverse("core:track_order"),
            {
                "order_number": order.order_number,
                "phone": "0500000000",
            },
        )
        self.assertNotContains(invalid_response, order.get_status_display())
        self.assertContains(invalid_response, "لم نعثر على طلب مطابق")

    def test_crops_and_tools_are_hidden_behind_catalog_sections(self):
        home = self.client.get(reverse("core:home"))
        self.assertContains(home, 'id="crop-collection"', count=1)
        self.assertContains(home, 'coffee-products-section" hidden', count=1)
        self.assertContains(home, 'id="tools-collection" class="section-space" hidden')

        crops = self.client.get(reverse("catalog:crops"))
        tools = self.client.get(reverse("catalog:tools"))
        for crop in (
            "شلشلي إثيوبي",
            "مزيج البهاء",
            "بلقيس اليمن",
            "روبي كلومبي",
            "قوجي إثيوبي",
            "سدرة جازان",
            "كينيا نيري",
            "برازيلي سانتوس",
        ):
            self.assertContains(crops, crop)

        for tool in (
            "أكواب إسبريسو",
            "مطحنة يدوية",
            "قمع تقطير",
            "ميزان قهوة",
            "فلاتر جميع المقاسات",
            "مطاحن القهوة",
            "أدوات التقطير",
            "أباريق التحضير",
            "ملحقات القهوة",
        ):
            self.assertContains(tools, tool)

    def test_brand_decoration_and_free_shipping_threshold(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, '<strong dir="ltr">A23</strong>', count=2)
        self.assertContains(response, "شحن مجاني للطلبات التي تتجاوز")
        self.assertContains(response, "150 ريال")
        self.assertNotContains(response, "250 ريال")

    def test_ai_widget_and_local_store_answers(self):
        home = self.client.get(reverse("core:home"))
        self.assertContains(home, "مساعد A23 الذكي")
        self.assertContains(home, reverse("core:ai_chat"))

        response = self.client.post(
            reverse("core:ai_chat"),
            data=json.dumps({"message": "كيف أتتبع طلبي؟"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["mode"], "local")
        self.assertIn("رقم الطلب", response.json()["answer"])

    def test_ai_chat_validates_input(self):
        empty_response = self.client.post(
            reverse("core:ai_chat"),
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        long_response = self.client.post(
            reverse("core:ai_chat"),
            data=json.dumps({"message": "س" * 601}),
            content_type="application/json",
        )
        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(long_response.status_code, 400)

        csrf_client = Client(enforce_csrf_checks=True)
        csrf_response = csrf_client.post(
            reverse("core:ai_chat"),
            data=json.dumps({"message": "مرحبًا"}),
            content_type="application/json",
        )
        self.assertEqual(csrf_response.status_code, 403)

    @mock.patch("core.views.requests.post")
    def test_ai_chat_uses_responses_api_when_configured(self, post):
        api_response = mock.Mock()
        api_response.raise_for_status.return_value = None
        api_response.json.return_value = {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "إجابة ذكية"}
                    ]
                }
            ]
        }
        post.return_value = api_response

        with self.settings(
            OPENAI_API_KEY="test-key",
            OPENAI_CHAT_MODEL="gpt-5.6-terra",
        ):
            response = self.client.post(
                reverse("core:ai_chat"),
                data=json.dumps({"message": "ما أفضل طريقة لتحضير القهوة؟"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"answer": "إجابة ذكية", "mode": "ai"})
        request_payload = post.call_args.kwargs["json"]
        self.assertEqual(request_payload["model"], "gpt-5.6-terra")
        self.assertFalse(request_payload["store"])
        self.assertTrue(request_payload["safety_identifier"])
