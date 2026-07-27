from django.conf import settings
from django.db import models
from django.db.models import Q


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.CASCADE,
        related_name="profile",
    )

    phone = models.CharField(
        verbose_name="رقم الهاتف",
        max_length=30,
        blank=True,
    )

    avatar = models.ImageField(
        verbose_name="الصورة الشخصية",
        upload_to="users/avatars/",
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField(
        verbose_name="تاريخ الميلاد",
        blank=True,
        null=True,
    )

    is_phone_verified = models.BooleanField(
        verbose_name="هل رقم الهاتف موثق؟",
        default=False,
    )

    marketing_consent = models.BooleanField(
        verbose_name="الموافقة على الرسائل التسويقية",
        default=False,
    )

    created_at = models.DateTimeField(
        verbose_name="تاريخ الإنشاء",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="تاريخ آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "الملف الشخصي"
        verbose_name_plural = "الملفات الشخصية"
        ordering = ["-created_at"]

    def __str__(self):
        full_name = self.user.get_full_name()

        if full_name:
            return full_name

        return self.user.get_username()


class Address(models.Model):
    class AddressType(models.TextChoices):
        HOME = "home", "المنزل"
        WORK = "work", "العمل"
        OTHER = "other", "أخرى"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    address_type = models.CharField(
        verbose_name="نوع العنوان",
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.HOME,
    )

    recipient_name = models.CharField(
        verbose_name="اسم المستلم",
        max_length=150,
    )

    phone = models.CharField(
        verbose_name="رقم هاتف المستلم",
        max_length=30,
    )

    country = models.CharField(
        verbose_name="الدولة",
        max_length=100,
        default="المملكة العربية السعودية",
    )

    city = models.CharField(
        verbose_name="المدينة",
        max_length=100,
    )

    district = models.CharField(
        verbose_name="الحي",
        max_length=100,
    )

    street = models.CharField(
        verbose_name="اسم الشارع",
        max_length=200,
    )

    building_number = models.CharField(
        verbose_name="رقم المبنى",
        max_length=50,
        blank=True,
    )

    postal_code = models.CharField(
        verbose_name="الرمز البريدي",
        max_length=20,
        blank=True,
    )

    additional_number = models.CharField(
        verbose_name="الرقم الإضافي",
        max_length=20,
        blank=True,
    )

    notes = models.TextField(
        verbose_name="ملاحظات العنوان",
        blank=True,
    )

    is_default = models.BooleanField(
        verbose_name="هل هو العنوان الافتراضي؟",
        default=False,
    )

    created_at = models.DateTimeField(
        verbose_name="تاريخ إضافة العنوان",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="تاريخ آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "العنوان"
        verbose_name_plural = "العناوين"
        ordering = ["-is_default", "-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="unique_default_address_per_user",
            ),
        ]

        indexes = [
            models.Index(
                fields=["user", "is_default"],
                name="address_user_default_idx",
            ),
            models.Index(
                fields=["city"],
                name="address_city_idx",
            ),
        ]

    def __str__(self):
        return f"{self.recipient_name} - {self.city} - {self.district}"

    def save(self, *args, **kwargs):
        if self.is_default and self.user_id:
            Address.objects.filter(
                user_id=self.user_id,
                is_default=True,
            ).exclude(
                pk=self.pk,
            ).update(
                is_default=False,
            )

        super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.CASCADE,
        related_name="wishlist",
    )

    created_at = models.DateTimeField(
        verbose_name="تاريخ إنشاء قائمة المفضلة",
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name="تاريخ آخر تحديث",
        auto_now=True,
    )

    class Meta:
        verbose_name = "قائمة المفضلة"
        verbose_name_plural = "قوائم المفضلة"
        ordering = ["-created_at"]

    def __str__(self):
        return f"قائمة مفضلة المستخدم: {self.user.get_username()}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        verbose_name="قائمة المفضلة",
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        "catalog.Product",
        verbose_name="المنتج",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    created_at = models.DateTimeField(
        verbose_name="تاريخ إضافة المنتج",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "منتج في قائمة المفضلة"
        verbose_name_plural = "منتجات قوائم المفضلة"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                name="unique_product_in_wishlist",
            ),
        ]

        indexes = [
            models.Index(
                fields=["wishlist", "created_at"],
                name="wishlist_created_idx",
            ),
        ]

    def __str__(self):
        return f"{self.product} - {self.wishlist}"