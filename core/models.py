from django.core.validators import MinValueValidator
from django.db import models


class SiteSetting(models.Model):
    site_name = models.CharField(
        "اسم المتجر",
        max_length=200,
    )

    site_description = models.TextField(
        "وصف المتجر",
        blank=True,
    )

    logo = models.ImageField(
        "شعار المتجر",
        upload_to="site/logos/",
        blank=True,
        null=True,
    )

    favicon = models.ImageField(
        "أيقونة الموقع",
        upload_to="site/favicon/",
        blank=True,
        null=True,
    )

    email = models.EmailField(
        "البريد الإلكتروني",
        blank=True,
    )

    phone = models.CharField(
        "رقم الهاتف",
        max_length=30,
        blank=True,
    )

    whatsapp = models.CharField(
        "رقم واتساب",
        max_length=30,
        blank=True,
    )

    address = models.TextField(
        "العنوان",
        blank=True,
    )

    currency = models.CharField(
        "العملة",
        max_length=10,
        default="SAR",
    )

    tax_percentage = models.DecimalField(
        "نسبة الضريبة",
        max_digits=5,
        decimal_places=2,
        default=15,
        validators=[MinValueValidator(0)],
    )

    is_maintenance_mode = models.BooleanField(
        "وضع الصيانة",
        default=False,
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
        verbose_name = "إعدادات المتجر"
        verbose_name_plural = "إعدادات المتجر"

    def __str__(self):
        return self.site_name


class Banner(models.Model):
    title = models.CharField(
        "عنوان الإعلان",
        max_length=200,
    )

    subtitle = models.CharField(
        "العنوان الفرعي",
        max_length=250,
        blank=True,
    )

    image = models.ImageField(
        "صورة الإعلان",
        upload_to="banners/",
    )

    button_text = models.CharField(
        "نص الزر",
        max_length=100,
        blank=True,
    )

    button_url = models.CharField(
        "رابط الزر",
        max_length=500,
        blank=True,
        help_text="يمكن إدخال رابط داخلي أو رابط خارجي آمن.",
    )

    display_order = models.PositiveIntegerField(
        "ترتيب العرض",
        default=0,
    )

    is_active = models.BooleanField(
        "نشط",
        default=True,
    )

    starts_at = models.DateTimeField(
        "بداية العرض",
        blank=True,
        null=True,
    )

    ends_at = models.DateTimeField(
        "نهاية العرض",
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
        verbose_name = "إعلان"
        verbose_name_plural = "الإعلانات"
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class StaticPage(models.Model):
    title = models.CharField(
        "عنوان الصفحة",
        max_length=200,
    )

    slug = models.SlugField(
        "الرابط المختصر",
        max_length=220,
        unique=True,
        allow_unicode=True,
    )

    content = models.TextField(
        "محتوى الصفحة",
    )

    meta_description = models.CharField(
        "وصف محركات البحث",
        max_length=300,
        blank=True,
    )

    is_active = models.BooleanField(
        "منشورة",
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
        verbose_name = "صفحة ثابتة"
        verbose_name_plural = "الصفحات الثابتة"
        ordering = ["title"]

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(
        "الاسم",
        max_length=150,
    )

    email = models.EmailField(
        "البريد الإلكتروني",
    )

    phone = models.CharField(
        "رقم الهاتف",
        max_length=30,
        blank=True,
    )

    subject = models.CharField(
        "موضوع الرسالة",
        max_length=200,
    )

    message = models.TextField(
        "نص الرسالة",
    )

    is_read = models.BooleanField(
        "تمت القراءة",
        default=False,
    )

    replied_at = models.DateTimeField(
        "تاريخ الرد",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإرسال",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.subject}"