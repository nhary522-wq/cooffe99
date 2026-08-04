from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from catalog.services import get_store_item
from payments.models import Payment, PaymentMethod

from .forms import CheckoutForm
from .models import Order, OrderItem, Shipment


FREE_SHIPPING_THRESHOLD = Decimal("150.00")
STANDARD_SHIPPING = Decimal("25.00")
EXPRESS_SHIPPING = Decimal("45.00")


def _safe_next(request, default_name="orders:cart"):
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse(default_name)


def _cart_summary(request, shipping_method="standard"):
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

    if shipping_method == "express":
        shipping = EXPRESS_SHIPPING
    elif subtotal > FREE_SHIPPING_THRESHOLD:
        shipping = Decimal("0.00")
    else:
        shipping = STANDARD_SHIPPING

    return {
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": subtotal + shipping,
        "free_shipping_remaining": max(
            Decimal("0.00"),
            FREE_SHIPPING_THRESHOLD - subtotal + Decimal("0.01"),
        ),
    }


@require_POST
def add_to_cart(request, slug):
    if not get_store_item(slug):
        raise Http404
    try:
        quantity = max(1, min(int(request.POST.get("quantity", 1)), 20))
    except (TypeError, ValueError):
        quantity = 1
    cart = request.session.get("cart", {})
    cart[slug] = min(int(cart.get(slug, 0)) + quantity, 20)
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
    selected_shipping = request.POST.get("shipping_method", "standard")
    summary = _cart_summary(request, selected_shipping)
    if not summary["items"]:
        messages.error(request, "السلة فارغة. أضف منتجًا قبل إتمام الطلب.")
        return redirect("catalog:product_list")

    if request.method == "POST" and form.is_valid():
        summary = _cart_summary(request, form.cleaned_data["shipping_method"])
        payment_labels = dict(CheckoutForm.PAYMENT_CHOICES)
        shipping_labels = dict(CheckoutForm.SHIPPING_CHOICES)
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
                customer_notes=(
                    "طريقة التوصيل: "
                    f"{shipping_labels[form.cleaned_data['shipping_method']]}"
                ),
            )
            for cart_item in summary["items"]:
                product = cart_item["product"]
                OrderItem.objects.create(
                    order=order,
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
                shipping_company=(
                    "التوصيل السريع"
                    if form.cleaned_data["shipping_method"] == "express"
                    else "التوصيل العادي"
                ),
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
