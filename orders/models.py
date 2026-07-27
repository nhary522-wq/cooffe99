import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.CASCADE,
        related_name="cart",
        blank=True,
        null=True,
    )

    session_key = models.CharField(
        "معرف جلسة الزائر",
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإنشاء",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "سلة تسوق"
        verbose_name_plural = "سلات التسوق"
        constraints = [
            models.CheckConstraint(
                condition=Q(user__isnull=False) | Q(session_key__isnull=False),
                name="cart_requires_user_or_session",
            ),
            models.UniqueConstraint(
                fields=["session_key"],
                condition=Q(session_key__isnull=False),
                name="unique_cart_session_key",
            ),
        ]

    def __str__(self):
        if self.user:
            return f"سلة {self.user.get_username()}"

        return f"سلة زائر {self.session_key}"

    @property
    def subtotal(self):
        return sum(
            (item.total_price for item in self.items.all()),
            Decimal("0.00"),
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        verbose_name="السلة",
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="المنتج",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )

    variant = models.ForeignKey(
        "catalog.ProductVariant",
        verbose_name="متغير المنتج",
        on_delete=models.SET_NULL,
        related_name="cart_items",
        blank=True,
        null=True,
    )

    quantity = models.PositiveIntegerField(
        "الكمية",
        default=1,
        validators=[MinValueValidator(1)],
    )

    created_at = models.DateTimeField(
        "تاريخ الإضافة",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "عنصر سلة"
        verbose_name_plural = "عناصر السلة"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product", "variant"],
                name="unique_product_variant_in_cart",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.effective_price

        return self.product.price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "نسبة مئوية"),
        ("fixed", "مبلغ ثابت"),
    ]

    code = models.CharField(
        "رمز الكوبون",
        max_length=50,
        unique=True,
        db_index=True,
    )

    discount_type = models.CharField(
        "نوع الخصم",
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
    )

    discount_value = models.DecimalField(
        "قيمة الخصم",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    minimum_order_amount = models.DecimalField(
        "الحد الأدنى للطلب",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    maximum_discount_amount = models.DecimalField(
        "الحد الأقصى للخصم",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    usage_limit = models.PositiveIntegerField(
        "عدد مرات الاستخدام المسموح",
        blank=True,
        null=True,
    )

    used_count = models.PositiveIntegerField(
        "عدد مرات الاستخدام",
        default=0,
    )

    starts_at = models.DateTimeField(
        "بداية الصلاحية",
    )

    expires_at = models.DateTimeField(
        "نهاية الصلاحية",
    )

    is_active = models.BooleanField(
        "نشط",
        default=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإنشاء",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "كوبون خصم"
        verbose_name_plural = "كوبونات الخصم"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(discount_value__gt=0),
                name="coupon_discount_value_gt_zero",
            ),
        ]

    def __str__(self):
        return self.code.upper()

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "قيد الانتظار"),
        ("confirmed", "تم التأكيد"),
        ("processing", "قيد التجهيز"),
        ("shipped", "تم الشحن"),
        ("delivered", "تم التسليم"),
        ("cancelled", "ملغي"),
        ("refunded", "تم الاسترداد"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "بانتظار الدفع"),
        ("paid", "مدفوع"),
        ("partially_refunded", "مسترد جزئيًا"),
        ("refunded", "مسترد بالكامل"),
        ("failed", "فشل الدفع"),
    ]

    order_number = models.CharField(
        "رقم الطلب",
        max_length=40,
        unique=True,
        editable=False,
        db_index=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.SET_NULL,
        related_name="orders",
        blank=True,
        null=True,
    )

    coupon = models.ForeignKey(
        Coupon,
        verbose_name="الكوبون",
        on_delete=models.SET_NULL,
        related_name="orders",
        blank=True,
        null=True,
    )

    status = models.CharField(
        "حالة الطلب",
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    payment_status = models.CharField(
        "حالة الدفع",
        max_length=30,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    customer_name = models.CharField(
        "اسم العميل",
        max_length=150,
    )

    customer_email = models.EmailField(
        "البريد الإلكتروني",
    )

    customer_phone = models.CharField(
        "رقم الهاتف",
        max_length=30,
    )

    shipping_country = models.CharField(
        "دولة الشحن",
        max_length=100,
        default="المملكة العربية السعودية",
    )

    shipping_city = models.CharField(
        "مدينة الشحن",
        max_length=100,
    )

    shipping_district = models.CharField(
        "حي الشحن",
        max_length=100,
    )

    shipping_street = models.CharField(
        "شارع الشحن",
        max_length=200,
    )

    shipping_building_number = models.CharField(
        "رقم المبنى",
        max_length=50,
        blank=True,
    )

    shipping_postal_code = models.CharField(
        "الرمز البريدي",
        max_length=20,
        blank=True,
    )

    shipping_notes = models.TextField(
        "ملاحظات الشحن",
        blank=True,
    )

    subtotal = models.DecimalField(
        "المجموع قبل الخصم",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    discount_amount = models.DecimalField(
        "قيمة الخصم",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    shipping_amount = models.DecimalField(
        "تكلفة الشحن",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    tax_amount = models.DecimalField(
        "قيمة الضريبة",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    total_amount = models.DecimalField(
        "إجمالي الطلب",
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    customer_notes = models.TextField(
        "ملاحظات العميل",
        blank=True,
    )

    admin_notes = models.TextField(
        "ملاحظات الإدارة",
        blank=True,
    )

    placed_at = models.DateTimeField(
        "تاريخ إنشاء الطلب",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["status", "placed_at"]),
            models.Index(fields=["payment_status", "placed_at"]),
            models.Index(fields=["customer_email"]),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"

        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="الطلب",
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="المنتج",
        on_delete=models.SET_NULL,
        related_name="order_items",
        blank=True,
        null=True,
    )

    variant = models.ForeignKey(
        "catalog.ProductVariant",
        verbose_name="متغير المنتج",
        on_delete=models.SET_NULL,
        related_name="order_items",
        blank=True,
        null=True,
    )

    product_name = models.CharField(
        "اسم المنتج وقت الشراء",
        max_length=220,
    )

    variant_name = models.CharField(
        "اسم المتغير وقت الشراء",
        max_length=150,
        blank=True,
    )

    sku = models.CharField(
        "رمز المنتج وقت الشراء",
        max_length=100,
    )

    unit_price = models.DecimalField(
        "سعر الوحدة",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    quantity = models.PositiveIntegerField(
        "الكمية",
        validators=[MinValueValidator(1)],
    )

    total_price = models.DecimalField(
        "الإجمالي",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلب"
        ordering = ["id"]

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("pending", "بانتظار الشحن"),
        ("prepared", "تم التجهيز"),
        ("shipped", "تم الشحن"),
        ("out_for_delivery", "خرج للتسليم"),
        ("delivered", "تم التسليم"),
        ("returned", "مرتجع"),
    ]

    order = models.OneToOneField(
        Order,
        verbose_name="الطلب",
        on_delete=models.CASCADE,
        related_name="shipment",
    )

    shipping_company = models.CharField(
        "شركة الشحن",
        max_length=150,
        blank=True,
    )

    tracking_number = models.CharField(
        "رقم التتبع",
        max_length=150,
        blank=True,
        db_index=True,
    )

    tracking_url = models.URLField(
        "رابط التتبع",
        blank=True,
    )

    status = models.CharField(
        "حالة الشحنة",
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
    )

    shipped_at = models.DateTimeField(
        "تاريخ الشحن",
        blank=True,
        null=True,
    )

    delivered_at = models.DateTimeField(
        "تاريخ التسليم",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإنشاء",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "شحنة"
        verbose_name_plural = "الشحنات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"شحنة {self.order.order_number}"