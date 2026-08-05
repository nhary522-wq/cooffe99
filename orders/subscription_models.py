from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .models import Order


class SubscriptionPlan(models.Model):
    FREQUENCIES = [("monthly", "شهري"), ("periodic", "دوري")]
    name = models.CharField("اسم الخطة", max_length=180)
    slug = models.SlugField("الرابط المختصر", max_length=200, unique=True, allow_unicode=True)
    description = models.TextField("الوصف")
    price = models.DecimalField("السعر", max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    duration_months = models.PositiveIntegerField("مدة الاشتراك بالأشهر", default=1)
    frequency = models.CharField("التكرار", max_length=15, choices=FREQUENCIES, default="monthly")
    interval_days = models.PositiveIntegerField("الفاصل بالأيام", default=30)
    product_count = models.PositiveIntegerField("عدد المنتجات", default=1)
    weight_grams = models.PositiveIntegerField("الوزن بالجرام", default=250)
    benefits = models.TextField("المزايا", blank=True)
    is_available = models.BooleanField("متاحة", default=True, db_index=True)
    max_subscribers = models.PositiveIntegerField("الحد الأقصى للمشتركين", null=True, blank=True)
    image = models.ImageField("الصورة", upload_to="subscriptions/plans/", blank=True)
    display_order = models.PositiveIntegerField("ترتيب الظهور", default=0)
    class Meta: app_label = "orders"; verbose_name = "خطة اشتراك"; verbose_name_plural = "خطط الاشتراك"; ordering = ["display_order", "name"]
    def __str__(self): return self.name


class Subscription(models.Model):
    STATUSES = [("pending", "بانتظار التفعيل"), ("active", "نشط"), ("paused", "متوقف مؤقتًا"), ("cancelled", "ملغي"), ("expired", "منتهي")]
    GRINDS = [("whole", "حبوب كاملة"), ("fine", "ناعم"), ("medium", "متوسط"), ("coarse", "خشن")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="المستخدم", on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(SubscriptionPlan, verbose_name="الخطة", on_delete=models.PROTECT, related_name="subscriptions")
    start_date = models.DateField("تاريخ البداية")
    next_shipment_at = models.DateTimeField("موعد الشحنة القادمة", db_index=True)
    address = models.ForeignKey("accounts.Address", verbose_name="العنوان", on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField("الحالة", max_length=15, choices=STATUSES, default="pending", db_index=True)
    coffee_preferences = models.TextField("تفضيلات القهوة", blank=True)
    grind_type = models.CharField("طريقة الطحن", max_length=15, choices=GRINDS, default="whole")
    excluded_products = models.ManyToManyField("catalog.Product", verbose_name="المنتجات المستبعدة", blank=True, related_name="excluded_from_subscriptions")
    paused_at = models.DateTimeField("تاريخ الإيقاف", null=True, blank=True)
    cancelled_at = models.DateTimeField("تاريخ الإلغاء", null=True, blank=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    class Meta: app_label = "orders"; verbose_name = "اشتراك"; verbose_name_plural = "الاشتراكات"; ordering = ["-created_at"]
    def __str__(self): return f"{self.user} - {self.plan}"


class SubscriptionBox(models.Model):
    STATUSES = [("scheduled", "مجدولة"), ("prepared", "مجهزة"), ("shipped", "مشحونة"), ("delivered", "مسلّمة"), ("cancelled", "ملغاة")]
    subscription = models.ForeignKey(Subscription, verbose_name="الاشتراك", on_delete=models.PROTECT, related_name="boxes")
    period_start = models.DateField("بداية الفترة")
    period_end = models.DateField("نهاية الفترة")
    scheduled_at = models.DateTimeField("موعد الشحن")
    order = models.OneToOneField(Order, verbose_name="الطلب", on_delete=models.SET_NULL, null=True, blank=True, related_name="subscription_box")
    status = models.CharField("الحالة", max_length=15, choices=STATUSES, default="scheduled")
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    class Meta:
        app_label = "orders"; verbose_name = "صندوق اشتراك"; verbose_name_plural = "صناديق الاشتراك"; ordering = ["-scheduled_at"]
        constraints = [models.UniqueConstraint(fields=["subscription", "period_start"], name="unique_subscription_period_box")]
    def __str__(self): return f"{self.subscription} - {self.period_start}"


class SubscriptionBoxItem(models.Model):
    box = models.ForeignKey(SubscriptionBox, verbose_name="الصندوق", on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("catalog.Product", verbose_name="المنتج", on_delete=models.PROTECT, related_name="subscription_box_items")
    quantity = models.PositiveIntegerField("الكمية", default=1, validators=[MinValueValidator(1)])
    class Meta:
        app_label = "orders"; verbose_name = "منتج صندوق"; verbose_name_plural = "منتجات الصناديق"
        constraints = [models.UniqueConstraint(fields=["box", "product"], name="unique_product_per_box")]
    def __str__(self): return f"{self.box} - {self.product}"
