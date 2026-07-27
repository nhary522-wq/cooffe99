import os
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegistrationForm, normalize_phone
from .models import Profile


def _safe_next_url(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse("core:home")


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = get_user_model().objects.create_user(
                username=f"customer_{uuid.uuid4().hex}",
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )
            Profile.objects.create(user=user, phone=form.cleaned_data["phone"])
        login(
            request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        messages.success(request, "تم إنشاء حسابك وتسجيل دخولك بنجاح.")
        return redirect(_safe_next_url(request))

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["identifier"].strip()
        user_model = get_user_model()
        user = None

        if "@" in identifier:
            user = user_model.objects.filter(email__iexact=identifier).first()
        else:
            phone = normalize_phone(identifier)
            profile = Profile.objects.select_related("user").filter(
                phone=phone,
            ).first()
            user = profile.user if profile else None

        authenticated_user = authenticate(
            request,
            username=user.get_username() if user else "",
            password=form.cleaned_data["password"],
        )
        if authenticated_user:
            login(request, authenticated_user)
            messages.success(request, "تم تسجيل دخولك بنجاح.")
            return redirect(_safe_next_url(request))
        form.add_error(None, "بيانات الدخول غير صحيحة.")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "تم تسجيل خروجك بنجاح.")
    return redirect("core:home")


def social_login(request, provider):
    providers = {
        "google": ("GOOGLE_CLIENT_ID", "google_login", "Google"),
        "apple": ("APPLE_CLIENT_ID", "apple_login", "Apple"),
    }
    config = providers.get(provider)
    if not config:
        return redirect("accounts:login")
    environment_key, route_name, display_name = config
    if not os.environ.get(environment_key):
        messages.error(
            request,
            f"تسجيل {display_name} يحتاج إضافة مفاتيح الربط في إعدادات الخادم.",
        )
        return redirect("accounts:login")
    return redirect(route_name)
