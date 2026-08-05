from django.shortcuts import render

# Create your views here.
import csv
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count, DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.models import LoyaltyTransaction
from catalog.models import Product, ProductReview
from orders.models import Order, OrderItem
from orders.subscription_models import Subscription


def _report(request):
    today = timezone.localdate(); start_raw = request.GET.get("start", "")[:10]; end_raw = request.GET.get("end", "")[:10]
    try: start = timezone.datetime.fromisoformat(start_raw).date() if start_raw else today - timedelta(days=30)
    except ValueError: start = today - timedelta(days=30)
    try: end = timezone.datetime.fromisoformat(end_raw).date() if end_raw else today
    except ValueError: end = today
    orders = Order.objects.filter(placed_at__date__range=(start, end))
    status = request.GET.get("status", "")[:30]
    if status: orders = orders.filter(status=status)
    paid = orders.filter(payment_status="paid")
    decimal_zero = Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
    summary = paid.aggregate(sales=Coalesce(Sum("total_amount"), decimal_zero), count=Count("id"), average=Coalesce(Avg("total_amount"), decimal_zero))
    return {"start": start, "end": end, "status": status, "summary": summary,
            "orders_by_status": orders.values("status").annotate(total=Count("id")).order_by("status"),
            "top_products": OrderItem.objects.filter(order__in=paid).values("product_name").annotate(quantity=Sum("quantity"), revenue=Sum("total_price")).order_by("-quantity")[:10],
            "low_stock": Product.objects.filter(is_active=True, track_stock=True, stock__lte=F("low_stock_threshold")).order_by("stock")[:20],
            "best_customers": paid.exclude(user=None).values("user__username").annotate(total=Sum("total_amount"), orders=Count("id")).order_by("-total")[:10],
            "active_subscriptions": Subscription.objects.filter(status="active").count(),
            "loyalty_usage": LoyaltyTransaction.objects.filter(created_at__date__range=(start, end)).aggregate(total=Coalesce(Sum("points"), 0))["total"],
            "review_average": ProductReview.objects.filter(is_approved=True).aggregate(value=Avg("rating"))["value"]}


@staff_member_required
def analytics(request): return render(request, "dashboard/analytics.html", _report(request))


@staff_member_required
def analytics_csv(request):
    report = _report(request); response = HttpResponse(content_type="text/csv; charset=utf-8"); response["Content-Disposition"] = 'attachment; filename="a23-report.csv"'; response.write("\ufeff")
    writer = csv.writer(response); writer.writerow(["المنتج", "الكمية", "الإيراد"])
    for row in report["top_products"]: writer.writerow([row["product_name"], row["quantity"], row["revenue"]])
    return response
