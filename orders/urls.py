from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("cart/add/<slug:slug>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<slug:slug>/", views.update_cart, name="update_cart"),
    path("cart/remove/<slug:slug>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("view/<str:order_number>/", views.order_detail, name="order_detail"),
]
