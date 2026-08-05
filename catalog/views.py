from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Prefetch, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductReviewForm
from .models import Product, ProductReview
from .services import get_store_item, get_store_items


def product_list(request, category=None):
    if category not in {None, "crops", "tools"}:
        raise Http404
    query = request.GET.get("q", "")[:100]
    category_titles = {
        None: "منتجات القهوة",
        "crops": "محاصيل القهوة",
        "tools": "أدوات القهوة",
    }
    return render(
        request,
        "catalog/product_list.html",
        {
            "items": get_store_items(category, query),
            "category": category,
            "category_title": category_titles[category],
            "query": query,
        },
    )


def product_detail(request, slug):
    product = (Product.objects.filter(slug=slug, is_active=True, is_published=True)
               .select_related("category", "brand")
               .prefetch_related("images", "attributes", "brew_methods", Prefetch("reviews", queryset=ProductReview.objects.filter(is_approved=True).select_related("user")))
               .annotate(average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True))).first())
    if product:
        related = (Product.objects.filter(category=product.category, is_active=True, is_published=True)
                   .exclude(pk=product.pk).select_related("category", "brand")[:3])
        own_review = ProductReview.objects.filter(product=product, user=request.user).first() if request.user.is_authenticated else None
        return render(request, "catalog/product_detail.html", {"product": product, "related_products": related, "review_form": ProductReviewForm(instance=own_review)})
    item = get_store_item(slug)
    if not item:
        raise Http404
    related_items = tuple(
        related
        for related in get_store_items(item["category"])
        if related["slug"] != slug
    )[:3]
    return render(
        request,
        "catalog/product_detail.html",
        {"item": item, "related_items": related_items},
    )


@login_required
@require_POST
def save_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True, is_published=True)
    review = ProductReview.objects.filter(product=product, user=request.user).first()
    form = ProductReviewForm(request.POST, instance=review)
    if form.is_valid():
        review = form.save(commit=False)
        review.product, review.user, review.is_approved = product, request.user, False
        review.is_verified_purchase = request.user.orders.filter(status="delivered", items__product=product).exists()
        review.save()
        messages.success(request, "تم حفظ المراجعة وستظهر بعد اعتمادها.")
    else:
        messages.error(request, "تحقق من بيانات المراجعة.")
    return redirect("catalog:product_detail", slug=slug)


def compare(request):
    ids = request.session.get("compare_products", [])
    products = list(Product.objects.filter(pk__in=ids, is_active=True, is_published=True).select_related("category", "brand").prefetch_related("brew_methods").annotate(average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True))))
    products.sort(key=lambda product: ids.index(product.pk))
    return render(request, "catalog/compare.html", {"products": products})


@require_POST
def compare_add(request, product_id):
    get_object_or_404(Product, pk=product_id, is_active=True, is_published=True)
    ids = request.session.get("compare_products", [])
    if product_id not in ids:
        if len(ids) >= 4:
            messages.error(request, "يمكن مقارنة أربعة منتجات كحد أقصى.")
        else:
            ids.append(product_id); request.session["compare_products"] = ids
    return redirect("catalog:compare")


@require_POST
def compare_remove(request, product_id):
    request.session["compare_products"] = [pk for pk in request.session.get("compare_products", []) if pk != product_id]
    return redirect("catalog:compare")
