from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
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


class TasteQuestion(models.Model):
    text = models.CharField("السؤال", max_length=300)
    key = models.SlugField("المعرف", max_length=80, unique=True)
    display_order = models.PositiveIntegerField("الترتيب", default=0)
    is_active = models.BooleanField("نشط", default=True)
    class Meta:
        verbose_name = "سؤال اختبار الذوق"; verbose_name_plural = "أسئلة اختبار الذوق"; ordering = ["display_order", "id"]
    def __str__(self): return self.text


class TasteAnswer(models.Model):
    question = models.ForeignKey(TasteQuestion, verbose_name="السؤال", on_delete=models.CASCADE, related_name="answers")
    text = models.CharField("الإجابة", max_length=180)
    value = models.CharField("القيمة", max_length=80)
    score_tags = models.CharField("وسوم المطابقة", max_length=250, blank=True)
    display_order = models.PositiveIntegerField("الترتيب", default=0)
    class Meta:
        verbose_name = "إجابة اختبار الذوق"; verbose_name_plural = "إجابات اختبار الذوق"; ordering = ["display_order", "id"]
        constraints = [models.UniqueConstraint(fields=["question", "value"], name="unique_taste_answer_value")]
    def __str__(self): return f"{self.question}: {self.text}"


class TasteProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="المستخدم", on_delete=models.CASCADE, related_name="taste_profile")
    profile_name = models.CharField("اسم ملف الذوق", max_length=120)
    preferences = models.JSONField("التفضيلات", default=dict)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    class Meta: verbose_name = "ملف ذوق"; verbose_name_plural = "ملفات الذوق"
    def __str__(self): return f"{self.user} - {self.profile_name}"


class CoffeeJournalEntry(models.Model):
    PRIVACY = [("private", "خاص"), ("public", "عام")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="المستخدم", on_delete=models.CASCADE, related_name="coffee_journal_entries")
    product = models.ForeignKey("catalog.Product", verbose_name="المنتج", on_delete=models.SET_NULL, null=True, blank=True, related_name="journal_entries")
    external_product_name = models.CharField("اسم منتج خارجي", max_length=220, blank=True)
    brew_method = models.ForeignKey("core.BrewMethod", verbose_name="طريقة التحضير", on_delete=models.SET_NULL, null=True, blank=True, related_name="journal_entries")
    experienced_at = models.DateTimeField("تاريخ التجربة")
    coffee_grams = models.DecimalField("كمية البن", max_digits=7, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.1)])
    water_ml = models.PositiveIntegerField("كمية الماء", null=True, blank=True)
    ratio = models.CharField("نسبة التحضير", max_length=30, blank=True)
    grind_size = models.CharField("درجة الطحن", max_length=120, blank=True)
    water_temperature = models.PositiveSmallIntegerField("درجة حرارة الماء", null=True, blank=True, validators=[MaxValueValidator(100)])
    extraction_seconds = models.PositiveIntegerField("مدة الاستخلاص", null=True, blank=True)
    overall_rating = models.PositiveSmallIntegerField("التقييم العام", validators=[MinValueValidator(1), MaxValueValidator(5)])
    acidity_rating = models.PositiveSmallIntegerField("الحموضة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    sweetness_rating = models.PositiveSmallIntegerField("الحلاوة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    body_rating = models.PositiveSmallIntegerField("القوام", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    flavor_rating = models.PositiveSmallIntegerField("النكهة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    notes = models.TextField("الملاحظات", blank=True)
    recipe = models.TextField("وصفة التحضير", blank=True)
    image = models.ImageField("صورة", upload_to="journal/", blank=True)
    privacy = models.CharField("الخصوصية", max_length=10, choices=PRIVACY, default="private", db_index=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    class Meta:
        verbose_name = "تجربة قهوة"; verbose_name_plural = "سجل القهوة الشخصي"; ordering = ["-experienced_at"]
        indexes = [models.Index(fields=["user", "experienced_at"], name="journal_user_date_idx"), models.Index(fields=["user", "overall_rating"], name="journal_user_rating_idx")]
        constraints = [models.CheckConstraint(condition=Q(product__isnull=False) | ~Q(external_product_name=""), name="journal_requires_product_name")]
    def __str__(self): return self.product.name if self.product else self.external_product_name


class SavedRecipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="المستخدم", on_delete=models.CASCADE, related_name="saved_recipes")
    source_entry = models.OneToOneField(CoffeeJournalEntry, verbose_name="التجربة الأصلية", on_delete=models.CASCADE, related_name="saved_recipe")
    title = models.CharField("العنوان", max_length=200)
    recipe = models.TextField("الوصفة")
    created_at = models.DateTimeField("تاريخ الحفظ", auto_now_add=True)
    class Meta: verbose_name = "وصفة محفوظة"; verbose_name_plural = "الوصفات المحفوظة"
    def __str__(self): return self.title


class LoyaltySetting(models.Model):
    is_enabled = models.BooleanField("النظام مفعل", default=True)
    points_per_riyal = models.DecimalField("نقاط لكل ريال", max_digits=7, decimal_places=2, default=1)
    bronze_min = models.PositiveIntegerField("حد البرونزي", default=0)
    silver_min = models.PositiveIntegerField("حد الفضي", default=500)
    gold_min = models.PositiveIntegerField("حد الذهبي", default=1500)
    platinum_min = models.PositiveIntegerField("حد البلاتيني", default=4000)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    class Meta: verbose_name = "إعدادات الولاء"; verbose_name_plural = "إعدادات الولاء"


class LoyaltyAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="المستخدم", on_delete=models.CASCADE, related_name="loyalty_account")
    balance = models.IntegerField("الرصيد", default=0, editable=False)
    lifetime_earned = models.PositiveIntegerField("إجمالي المكتسب", default=0, editable=False)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    class Meta: verbose_name = "حساب ولاء"; verbose_name_plural = "حسابات الولاء"
    def __str__(self): return str(self.user)


class LoyaltyTransaction(models.Model):
    TYPES = [("earn", "اكتساب"), ("redeem", "استخدام"), ("reverse", "عكس"), ("expire", "انتهاء")]
    account = models.ForeignKey(LoyaltyAccount, verbose_name="الحساب", on_delete=models.PROTECT, related_name="transactions")
    order = models.ForeignKey("orders.Order", verbose_name="الطلب", on_delete=models.PROTECT, null=True, blank=True, related_name="loyalty_transactions")
    transaction_type = models.CharField("نوع الحركة", max_length=12, choices=TYPES)
    points = models.IntegerField("النقاط")
    description = models.CharField("البيان", max_length=250)
    expires_at = models.DateTimeField("تنتهي في", null=True, blank=True)
    created_at = models.DateTimeField("تاريخ الحركة", auto_now_add=True)
    class Meta:
        verbose_name = "حركة نقاط"; verbose_name_plural = "حركات النقاط"; ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["order", "transaction_type"], condition=Q(order__isnull=False), name="unique_loyalty_order_type")]
    def __str__(self): return f"{self.account} {self.points}"
