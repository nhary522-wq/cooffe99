import os
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from catalog.models import Product
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CoffeeJournalForm, LoginForm, RegistrationForm, normalize_phone
from .models import CoffeeJournalEntry, LoyaltyAccount, Profile, SavedRecipe, TasteProfile, TasteQuestion


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


def taste_quiz(request):
    questions = TasteQuestion.objects.filter(is_active=True).prefetch_related("answers")
    if request.method == "POST":
        preferences, tags = {}, []
        for question in questions:
            answer = next((a for a in question.answers.all() if str(a.pk) == request.POST.get(f"question_{question.pk}")), None)
            if not answer:
                messages.error(request, "يرجى الإجابة عن جميع الأسئلة."); return render(request, "accounts/taste_quiz.html", {"questions": questions})
            preferences[question.key] = answer.value; tags.extend(t.strip().lower() for t in answer.score_tags.split(",") if t.strip())
        profile_name = "فاكهي منعش" if "fruity" in tags else "شوكولاتي متوازن" if "chocolate" in tags else "قوي وكثيف" if "dark" in tags else "ناعم قليل الحموضة"
        products = Product.objects.filter(is_active=True, is_published=True).filter(Q(track_stock=False) | Q(stock__gt=0)).select_related("category", "brand")
        scored = []
        for product in products:
            haystack = " ".join([product.flavor_notes, product.roast_level, product.suitable_brew_methods]).lower(); matching = [tag for tag in tags if tag in haystack]
            scored.append((len(matching), product, "، ".join(matching[:3]) or "متوفر ويتناسب مع اختياراتك العامة"))
        recommendations = sorted(scored, key=lambda row: (-row[0], row[1].price))[:6]
        request.session["taste_result"] = {"profile_name": profile_name, "preferences": preferences}
        if request.user.is_authenticated and "save" in request.POST: TasteProfile.objects.update_or_create(user=request.user, defaults={"profile_name": profile_name, "preferences": preferences})
        return render(request, "accounts/taste_result.html", {"profile_name": profile_name, "recommendations": recommendations})
    return render(request, "accounts/taste_quiz.html", {"questions": questions})


@login_required
def journal_list(request):
    entries = CoffeeJournalEntry.objects.filter(user=request.user).select_related("product", "brew_method")
    query, rating = request.GET.get("q", "")[:100], request.GET.get("rating", "")[:1]
    if query: entries = entries.filter(Q(product__name__icontains=query) | Q(external_product_name__icontains=query) | Q(notes__icontains=query))
    if rating.isdigit(): entries = entries.filter(overall_rating=int(rating))
    return render(request, "accounts/journal_list.html", {"entries": entries})


@login_required
def journal_edit(request, pk=None):
    entry = get_object_or_404(CoffeeJournalEntry, pk=pk, user=request.user) if pk else None; form = CoffeeJournalForm(request.POST or None, request.FILES or None, instance=entry)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False); obj.user = request.user; obj.save(); return redirect("accounts:journal_detail", pk=obj.pk)
    return render(request, "accounts/journal_form.html", {"form": form, "entry": entry})


@login_required
def journal_detail(request, pk): return render(request, "accounts/journal_detail.html", {"entry": get_object_or_404(CoffeeJournalEntry.objects.select_related("product", "brew_method"), pk=pk, user=request.user)})

@login_required
@require_POST
def journal_delete(request, pk): get_object_or_404(CoffeeJournalEntry, pk=pk, user=request.user).delete(); return redirect("accounts:journal_list")

@login_required
@require_POST
def journal_duplicate(request, pk):
    source = get_object_or_404(CoffeeJournalEntry, pk=pk, user=request.user); source.pk = None; source.image = None; source.save(); return redirect("accounts:journal_edit", pk=source.pk)

@login_required
@require_POST
def journal_to_recipe(request, pk):
    entry = get_object_or_404(CoffeeJournalEntry, pk=pk, user=request.user); SavedRecipe.objects.update_or_create(source_entry=entry, defaults={"user": request.user, "title": str(entry), "recipe": entry.recipe or entry.notes}); return redirect("accounts:journal_detail", pk=pk)

@login_required
def loyalty(request):
    account, _ = LoyaltyAccount.objects.get_or_create(user=request.user); return render(request, "accounts/loyalty.html", {"account": account, "transactions": account.transactions.select_related("order")[:100]})
