from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("crops/", views.product_list, {"category": "crops"}, name="crops"),
    path("tools/", views.product_list, {"category": "tools"}, name="tools"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
]
