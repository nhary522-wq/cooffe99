from django.urls import path

from django.urls import path
from . import views

app_name = "dashboard"
urlpatterns = [path("", views.analytics, name="analytics"), path("export.csv", views.analytics_csv, name="analytics_csv")]
