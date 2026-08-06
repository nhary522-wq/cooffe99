from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("crops/", views.product_list, {"category": "crops"}, name="crops"),
    path("tools/", views.product_list, {"category": "tools"}, name="tools"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("product/<slug:slug>/review/", views.save_review, name="save_review"),
    path("compare/", views.compare, name="compare"),
    path("compare/add/<int:product_id>/", views.compare_add, name="compare_add"),
    path("compare/remove/<int:product_id>/", views.compare_remove, name="compare_remove"),
    path("admin-import/<str:kind>/", views.import_catalog, name="import_catalog"),
    path("brand/<slug:slug>/", views.brand_detail, name="brand_detail"),
    path("card/<slug:slug>/", views.digital_card, name="digital_card"),
]
