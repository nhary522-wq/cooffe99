import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class PaymentMethod(models.Model):
    METHOD_TYPE_CHOICES = [
        ("card", "بطاقة بنكية"),
        ("mada", "مدى"),
        ("apple_pay", "Apple Pay"),
        ("stc_pay", "STC Pay"),
        ("bank_transfer", "تحويل بنكي"),
        ("cash_on_delivery", "الدفع عند الاستلام"),
        ("other", "أخرى"),
    ]

    name = models.CharField(
        "اسم وسيلة الدفع",
        max_length=100,
    )

    method_type = models.CharField(
        "نوع وسيلة الدفع",
        max_length=30,
        choices=METHOD_TYPE_CHOICES,
        unique=True,
    )

    description = models.TextField(
        "الوصف",
        blank=True,
    )

    icon = models.ImageField(
        "الأيقونة",
        upload_to="payments/methods/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(
        "نشطة",
        default=True,
    )

    display_order = models.PositiveIntegerField(
        "ترتيب العرض",
        default=0,
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
        verbose_name = "وسيلة دفع"
        verbose_name_plural = "وسائل الدفع"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "قيد الانتظار"),
        ("processing", "قيد المعالجة"),
        ("paid", "مدفوع"),
        ("failed", "فشل الدفع"),
        ("cancelled", "ملغي"),
        ("partially_refunded", "مسترد جزئيًا"),
        ("refunded", "مسترد بالكامل"),
    ]

    transaction_id = models.CharField(
        "رقم العملية",
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
    )

    order = models.ForeignKey(
        "orders.Order",
        verbose_name="الطلب",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        verbose_name="وسيلة الدفع",
        on_delete=models.PROTECT,
        related_name="payments",
    )

    status = models.CharField(
        "حالة الدفع",
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    amount = models.DecimalField(
        "المبلغ",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    currency = models.CharField(
        "العملة",
        max_length=10,
        default="SAR",
    )

    gateway_reference = models.CharField(
        "مرجع بوابة الدفع",
        max_length=250,
        blank=True,
        db_index=True,
    )

    gateway_name = models.CharField(
        "اسم بوابة الدفع",
        max_length=100,
        blank=True,
    )

    failure_reason = models.TextField(
        "سبب فشل الدفع",
        blank=True,
    )

    paid_at = models.DateTimeField(
        "تاريخ الدفع",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        "تاريخ إنشاء العملية",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "عملية دفع"
        verbose_name_plural = "عمليات الدفع"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["order", "status"]),
        ]

    def __str__(self):
        return self.transaction_id

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{uuid.uuid4().hex[:16].upper()}"

        super().save(*args, **kwargs)


class Refund(models.Model):
    STATUS_CHOICES = [
        ("requested", "تم طلب الاسترداد"),
        ("processing", "قيد المعالجة"),
        ("completed", "مكتمل"),
        ("rejected", "مرفوض"),
        ("failed", "فشل"),
    ]

    refund_number = models.CharField(
        "رقم الاسترداد",
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
    )

    payment = models.ForeignKey(
        Payment,
        verbose_name="عملية الدفع",
        on_delete=models.PROTECT,
        related_name="refunds",
    )

    amount = models.DecimalField(
        "المبلغ المسترد",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    reason = models.TextField(
        "سبب الاسترداد",
    )

    status = models.CharField(
        "حالة الاسترداد",
        max_length=30,
        choices=STATUS_CHOICES,
        default="requested",
        db_index=True,
    )

    gateway_reference = models.CharField(
        "مرجع بوابة الدفع",
        max_length=250,
        blank=True,
    )

    admin_notes = models.TextField(
        "ملاحظات الإدارة",
        blank=True,
    )

    completed_at = models.DateTimeField(
        "تاريخ اكتمال الاسترداد",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الطلب",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        "آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "عملية استرداد"
        verbose_name_plural = "عمليات الاسترداد"
        ordering = ["-created_at"]

    def __str__(self):
        return self.refund_number

    def save(self, *args, **kwargs):
        if not self.refund_number:
            self.refund_number = f"REF-{uuid.uuid4().hex[:16].upper()}"

        super().save(*args, **kwargs)