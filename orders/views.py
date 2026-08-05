from decimal import Decimal

from django.contrib import messages
from django.db import models, transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import datetime, time, timedelta
from .forms import SubscriptionForm
from .subscription_models import Subscription, SubscriptionPlan
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from catalog.services import get_store_item
from catalog.models import Product
from payments.models import Payment, PaymentMethod

from .forms import CheckoutForm
from .models import Order, OrderItem, Shipment


SHIPPING_COST = Decimal("20.00")


def _safe_next(request, default_name="orders:cart"):
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse(default_name)


def _cart_summary(request):
    cart = request.session.get("cart", {})
    items = []
    subtotal = Decimal("0.00")
    for slug, quantity in cart.items():
        item = get_store_item(slug)
        if not item:
            continue
        try:
            safe_quantity = max(1, min(int(quantity), 20))
        except (TypeError, ValueError):
            safe_quantity = 1
        total = item["price"] * safe_quantity
        items.append({"product": item, "quantity": safe_quantity, "total": total})
        subtotal += total

    shipping = SHIPPING_COST if items else Decimal("0.00")

    return {
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": subtotal + shipping,
    }


@require_POST
def add_to_cart(request, slug):
    item = get_store_item(slug)
    if not item:
        raise Http404
    try:
        quantity = max(1, min(int(request.POST.get("quantity", 1)), 20))
    except (TypeError, ValueError):
        quantity = 1
    available = min(int(item.get("stock", 20)), 20)
    if available < 1:
        messages.error(request, "المنتج غير متوفر حاليًا.")
        return redirect(_safe_next(request))
    cart = request.session.get("cart", {})
    cart[slug] = min(int(cart.get(slug, 0)) + quantity, available)
    request.session["cart"] = cart
    messages.success(request, "تمت إضافة المنتج إلى السلة.")
    return redirect(_safe_next(request))


def cart(request):
    return render(request, "orders/cart.html", _cart_summary(request))


@require_POST
def update_cart(request, slug):
    cart_data = request.session.get("cart", {})
    if slug not in cart_data:
        raise Http404
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity <= 0:
        cart_data.pop(slug, None)
    else:
        cart_data[slug] = min(quantity, 20)
    request.session["cart"] = cart_data
    return redirect("orders:cart")


@require_POST
def remove_from_cart(request, slug):
    cart_data = request.session.get("cart", {})
    cart_data.pop(slug, None)
    request.session["cart"] = cart_data
    messages.success(request, "تم حذف المنتج من السلة.")
    return redirect("orders:cart")


def checkout(request):
    initial = {}
    if request.user.is_authenticated:
        initial = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "email": request.user.email,
        }
        if hasattr(request.user, "profile"):
            initial["phone"] = request.user.profile.phone

    form = CheckoutForm(request.POST or None, initial=initial)
    summary = _cart_summary(request)
    if not summary["items"]:
        messages.error(request, "السلة فارغة. أضف منتجًا قبل إتمام الطلب.")
        return redirect("catalog:product_list")

    if request.method == "POST" and form.is_valid():
        summary = _cart_summary(request)
        payment_labels = dict(CheckoutForm.PAYMENT_CHOICES)
        method_type = form.cleaned_data["payment_method"]
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=(
                    f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"
                ),
                customer_email=form.cleaned_data["email"],
                customer_phone=form.cleaned_data["phone"],
                shipping_city=form.cleaned_data["city"],
                shipping_district=form.cleaned_data["district"],
                shipping_street=form.cleaned_data["street"],
                shipping_building_number=form.cleaned_data["building_number"],
                shipping_postal_code=form.cleaned_data["postal_code"],
                shipping_notes=form.cleaned_data["notes"],
                subtotal=summary["subtotal"],
                shipping_amount=summary["shipping"],
                total_amount=summary["total"],
                status="confirmed" if method_type == "cash_on_delivery" else "pending",
                payment_status="pending",
                customer_notes="التوصيل لجميع مناطق المملكة بقيمة 20 ريال.",
            )
            for cart_item in summary["items"]:
                product = cart_item["product"]
                db_product = Product.objects.select_for_update().filter(slug=product["slug"], is_active=True, is_published=True).first()
                if db_product and db_product.track_stock:
                    if db_product.stock < cart_item["quantity"]:
                        raise ValueError("المخزون المتاح لا يكفي لإتمام الطلب.")
                    db_product.stock -= cart_item["quantity"]
                    db_product.save(update_fields=["stock", "updated_at"])
                OrderItem.objects.create(
                    order=order,
                    product=db_product,
                    product_name=product["name"],
                    sku=product["slug"].upper(),
                    unit_price=product["price"],
                    quantity=cart_item["quantity"],
                    total_price=cart_item["total"],
                )

            payment_method, _ = PaymentMethod.objects.get_or_create(
                method_type=method_type,
                defaults={
                    "name": payment_labels[method_type],
                    "description": "وسيلة دفع متجر A23",
                    "is_active": True,
                },
            )
            Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=summary["total"],
                status="pending",
                gateway_name=(
                    "الدفع عند الاستلام"
                    if method_type == "cash_on_delivery"
                    else "بانتظار ربط بوابة الدفع"
                ),
            )
            Shipment.objects.create(
                order=order,
                shipping_company="التوصيل لجميع مناطق المملكة",
                status="pending",
            )

        placed_orders = request.session.get("placed_orders", [])
        request.session["placed_orders"] = (placed_orders + [order.pk])[-20:]
        request.session["cart"] = {}
        messages.success(request, "شكرًا لك، تم استلام طلبك بنجاح.")
        return redirect("orders:order_detail", order_number=order.order_number)

    context = {**summary, "form": form}
    return render(request, "orders/checkout.html", context)


def order_detail(request, order_number):
    order = get_object_or_404(
        Order.objects.select_related("shipment")
        .prefetch_related("items", "payments__payment_method"),
        order_number=order_number,
    )
    owns_order = request.user.is_authenticated and order.user_id == request.user.id
    session_order = order.pk in request.session.get("placed_orders", [])
    if not owns_order and not session_order:
        raise Http404
    return render(request, "orders/order_detail.html", {"order": order})


def subscription_plans(request):
    plans = SubscriptionPlan.objects.filter(is_available=True).annotate(active_count=models.Count("subscriptions", filter=models.Q(subscriptions__status="active")))
    return render(request, "orders/subscription_plans.html", {"plans": plans})


@login_required
def subscription_create(request, slug):
    plan = get_object_or_404(SubscriptionPlan, slug=slug, is_available=True)
    form = SubscriptionForm(request.POST or None)
    form.fields["address"].queryset = request.user.addresses.all()
    form.fields["excluded_products"].queryset = form.fields["excluded_products"].queryset.filter(is_active=True, is_published=True)
    if request.method == "POST" and form.is_valid():
        subscription = form.save(commit=False); subscription.user = request.user; subscription.plan = plan
        start = form.cleaned_data["start_date"]; subscription.next_shipment_at = timezone.make_aware(datetime.combine(start, time(hour=9))); subscription.status = "pending"; subscription.save(); form.save_m2m()
        messages.success(request, "تم إنشاء الاشتراك بحالة انتظار التفعيل؛ لم يُفترض نجاح أي دفع."); return redirect("orders:subscription_detail", pk=subscription.pk)
    return render(request, "orders/subscription_form.html", {"form": form, "plan": plan})


@login_required
def subscription_detail(request, pk):
    subscription = get_object_or_404(Subscription.objects.select_related("plan", "address").prefetch_related("boxes__items__product"), pk=pk, user=request.user)
    return render(request, "orders/subscription_detail.html", {"subscription": subscription})


@login_required
@require_POST
def subscription_action(request, pk, action):
    subscription = get_object_or_404(Subscription, pk=pk, user=request.user)
    now = timezone.now()
    if action == "pause" and subscription.status == "active": subscription.status, subscription.paused_at = "paused", now
    elif action == "resume" and subscription.status == "paused": subscription.status, subscription.paused_at, subscription.next_shipment_at = "active", None, now + timedelta(days=subscription.plan.interval_days)
    elif action == "cancel" and subscription.status in {"pending", "active", "paused"}: subscription.status, subscription.cancelled_at = "cancelled", now
    else: messages.error(request, "لا يمكن تنفيذ العملية في الحالة الحالية."); return redirect("orders:subscription_detail", pk=pk)
    subscription.save(update_fields=["status", "paused_at", "cancelled_at", "next_shipment_at", "updated_at"]); return redirect("orders:subscription_detail", pk=pk)
