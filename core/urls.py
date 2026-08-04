from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("assistant/chat/", views.ai_chat, name="ai_chat"),
    path("customer-service/contact/", views.contact, name="contact"),
    path("customer-service/faq/", views.faq, name="faq"),
    path(
        "customer-service/shipping/",
        views.shipping_policy,
        name="shipping_policy",
    ),
    path(
        "customer-service/returns/",
        views.return_policy,
        name="return_policy",
    ),
    path(
        "customer-service/track-order/",
        views.track_order,
        name="track_order",
    ),
]
