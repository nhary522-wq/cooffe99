from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Prefetch, Q
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CatalogCSVUploadForm, ProductReviewForm
from .importers import parse_catalog_csv, save_catalog_rows
from .models import Brand, Product, ProductReview
from .domain_models import ProcessingMethod, ToolSpecification
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
    items = get_store_items(category, query)
    filters = {key: request.GET.get(key, "")[:100] for key in ("brand", "country", "region", "variety", "processing", "roast", "material", "color", "availability")}
    price_min, price_max = request.GET.get("price_min", "")[:20], request.GET.get("price_max", "")[:20]
    if any(filters.values()) or price_min or price_max:
        products = Product.objects.filter(is_active=True, is_published=True).select_related("category", "brand").prefetch_related("tool_spec_values__specification")
        if category == "crops": products=products.filter(Q(product_type="crop")|Q(category__slug__icontains="crop"))
        elif category == "tools": products=products.filter(Q(product_type="tool")|Q(category__slug__icontains="tool"))
        if query: products=products.filter(Q(name__icontains=query)|Q(description__icontains=query)|Q(flavor_notes__icontains=query))
        if filters["brand"]: products=products.filter(brand__slug=filters["brand"])
        for key in ("country","region","variety","roast_level"):
            value=filters["roast"] if key=="roast_level" else filters.get(key)
            if value: products=products.filter(**{key:value})
        if filters["processing"]: products=products.filter(crop_profile__processing_method__slug=filters["processing"])
        if filters["material"]: products=products.filter(tool_profile__material__icontains=filters["material"])
        if filters["color"]: products=products.filter(tool_profile__color__icontains=filters["color"])
        if filters["availability"]=="available": products=products.filter(Q(track_stock=False)|Q(stock__gt=0))
        try:
            if price_min: products=products.filter(price__gte=price_min)
            if price_max: products=products.filter(price__lte=price_max)
        except (TypeError, ValueError): products=products.none()
        items=[{"slug":p.slug,"name":p.name,"category":p.product_type,"origin":p.country or p.country_of_manufacture or p.category.name,"price":p.price,"image":p.main_image.url if p.main_image else "/static/images/tools/coffee-accessories.webp","description":p.short_description or p.description} for p in products.distinct()]
    page=Paginator(items,12).get_page(request.GET.get("page"))
    return render(
        request,
        "catalog/product_list.html",
        {
            "items": page,
            "category": category,
            "category_title": category_titles[category],
            "query": query,
            "filters": filters,
            "brands": Brand.objects.filter(is_active=True).order_by("display_order","name"),
            "processing_methods": ProcessingMethod.objects.filter(is_active=True),
        },
    )


def product_detail(request, slug):
    product = (Product.objects.filter(slug=slug, is_active=True, is_published=True)
               .select_related("category", "brand", "crop_profile__processing_method", "tool_profile__manufacturer")
               .prefetch_related("images", "attributes", "brew_methods", "variants__commercial", "grind_options__option", "brew_recipes__brew_method", "journey_stages", "tool_spec_values__specification", "compatibilities_from__target", Prefetch("reviews", queryset=ProductReview.objects.filter(is_approved=True).select_related("user")))
               .annotate(average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True))).first())
    if product:
        related = (Product.objects.filter(category=product.category, is_active=True, is_published=True)
                   .exclude(pk=product.pk).select_related("category", "brand")[:3])
        own_review = ProductReview.objects.filter(product=product, user=request.user).first() if request.user.is_authenticated else None
        same_brand=Product.objects.filter(brand=product.brand,is_active=True,is_published=True).exclude(pk=product.pk)[:4] if product.brand_id else []
        return render(request, "catalog/product_detail.html", {"product": product, "related_products": related, "same_brand":same_brand, "review_form": ProductReviewForm(instance=own_review)})
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
    products = list(Product.objects.filter(pk__in=ids, is_active=True, is_published=True).select_related("category", "brand", "tool_profile", "crop_profile__processing_method").prefetch_related("brew_methods").annotate(average_rating=Avg("reviews__rating", filter=Q(reviews__is_approved=True))))
    products.sort(key=lambda product: ids.index(product.pk))
    comparison_kind=products[0].product_type if products else ""
    return render(request, "catalog/compare.html", {"products": products,"comparison_kind":comparison_kind})


@require_POST
def compare_add(request, product_id):
    product=get_object_or_404(Product, pk=product_id, is_active=True, is_published=True)
    ids = request.session.get("compare_products", [])
    if product_id not in ids:
        existing_type=Product.objects.filter(pk__in=ids).values_list("product_type",flat=True).first()
        if existing_type and existing_type != product.product_type:
            messages.error(request,"قارن منتجات من النوع نفسه؛ لا يمكن خلط المحاصيل بالأدوات.")
        elif len(ids) >= 4:
            messages.error(request, "يمكن مقارنة أربعة منتجات كحد أقصى.")
        else:
            ids.append(product_id); request.session["compare_products"] = ids
    return redirect("catalog:compare")


@require_POST
def compare_remove(request, product_id):
    request.session["compare_products"] = [pk for pk in request.session.get("compare_products", []) if pk != product_id]
    return redirect("catalog:compare")


@staff_member_required
def import_catalog(request, kind):
    if kind not in {"crops", "tools"}: raise Http404
    rows=errors=[]; form=CatalogCSVUploadForm(request.POST or None, request.FILES or None)
    session_key=f"catalog_import_{kind}"
    if request.method == "POST" and "confirm" in request.POST:
        rows=request.session.get(session_key, [])
        if not rows: messages.error(request,"انتهت المعاينة؛ ارفع الملف مجددًا.")
        else:
            created,updated=save_catalog_rows(rows,kind); request.session.pop(session_key,None)
            messages.success(request,f"تم الاستيراد: {created} جديد و{updated} محدّث."); return redirect("admin:catalog_product_changelist")
    elif request.method == "POST" and form.is_valid():
        try: rows,errors=parse_catalog_csv(form.cleaned_data["file"],kind)
        except (UnicodeDecodeError, ValueError) as exc: errors=[{"row":1,"message":str(exc)}]
        if not errors: request.session[session_key]=rows
    return render(request,"catalog/import_preview.html",{"form":form,"rows":rows,"errors":errors,"kind":kind})


def brand_detail(request, slug):
    brand=get_object_or_404(Brand,slug=slug,is_active=True)
    products=brand.products.filter(is_active=True,is_published=True).select_related("category")
    return render(request,"catalog/brand_detail.html",{"brand":brand,"products":products})


def digital_card(request, slug):
    product=get_object_or_404(Product.objects.filter(is_active=True,is_published=True).select_related("brand","category","crop_profile__processing_method").prefetch_related("roast_batches","brew_recipes__brew_method","reviews"),slug=slug,product_type="crop")
    return render(request,"catalog/digital_card.html",{"product":product,"latest_batch":product.roast_batches.first()})
