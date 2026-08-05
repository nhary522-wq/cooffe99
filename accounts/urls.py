from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("taste/", views.taste_quiz, name="taste_quiz"), path("journal/", views.journal_list, name="journal_list"), path("journal/add/", views.journal_edit, name="journal_add"),
    path("journal/<int:pk>/", views.journal_detail, name="journal_detail"), path("journal/<int:pk>/edit/", views.journal_edit, name="journal_edit"), path("journal/<int:pk>/delete/", views.journal_delete, name="journal_delete"),
    path("journal/<int:pk>/duplicate/", views.journal_duplicate, name="journal_duplicate"), path("journal/<int:pk>/recipe/", views.journal_to_recipe, name="journal_to_recipe"), path("loyalty/", views.loyalty, name="loyalty"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("social/<str:provider>/", views.social_login, name="social_login"),
]
