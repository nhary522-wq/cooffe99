
from decimal import Decimal

from cloudinary.models import CloudinaryField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


# =============================================================================
# التصنيفات
# =============================================================================


class Category(models.Model):
    name = models.CharField(
        "اسم التصنيف",
        max_length=150,
    )

    slug = models.SlugField(
        "الرابط المختصر",
        max_length=170,
        unique=True,
        allow_unicode=True,
        blank=True,
    )

    parent = models.ForeignKey(
        "self",
        verbose_name="التصنيف الأب",
        on_delete=models.SET_NULL,
        related_name="children",
        blank=True,
        null=True,
    )

    description = models.TextField(
        "وصف التصنيف",
        blank=True,
    )

    image = CloudinaryField(
        "صورة التصنيف",
        resource_type="image",
        folder="cooffe99/categories",
        blank=True,
        null=True,
    )

    display_order = models.PositiveIntegerField(
        "ترتيب العرض",
        default=0,
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
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"
        ordering = ["display_order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_name_per_parent",
            ),
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent} ← {self.name}"

        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                self.name,
                allow_unicode=True,
            )

            slug = base_slug
            counter = 1

            while (
                Category.objects
                .filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# =============================================================================
# العلامات التجارية
# =============================================================================


class Brand(models.Model):
    name = models.CharField(
        "اسم العلامة التجارية",
        max_length=150,
        unique=True,
    )

    slug = models.SlugField(
        "الرابط المختصر",
        max_length=170,
        unique=True,
        allow_unicode=True,
        blank=True,
    )

    description = models.TextField(
        "الوصف",
        blank=True,
    )

    logo = CloudinaryField(
        "شعار العلامة التجارية",
        resource_type="image",
        folder="cooffe99/brands",
        blank=True,
        null=True,
    )

    website_url = models.URLField(
        "الموقع الإلكتروني",
        blank=True,
    )

    is_active = models.BooleanField(
        "نشطة",
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
        verbose_name = "علامة تجارية"
        verbose_name_plural = "العلامات التجارية"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                self.name,
                allow_unicode=True,
            )

            slug = base_slug
            counter = 1

            while (
                Brand.objects
                .filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


# =============================================================================
# المنتجات
# =============================================================================


class Product(models.Model):
    ROAST_CHOICES = [("light", "فاتح"), ("medium", "متوسط"), ("dark", "غامق")]
    PROCESS_CHOICES = [("washed", "مغسولة"), ("natural", "مجففة"), ("honey", "عسلية"), ("other", "أخرى")]
    category = models.ForeignKey(
        Category,
        verbose_name="التصنيف",
        on_delete=models.PROTECT,
        related_name="products",
    )

    brand = models.ForeignKey(
        Brand,
        verbose_name="العلامة التجارية",
        on_delete=models.SET_NULL,
        related_name="products",
        blank=True,
        null=True,
    )

    name = models.CharField(
        "اسم المنتج",
        max_length=220,
    )

    slug = models.SlugField(
        "الرابط المختصر",
        max_length=250,
        unique=True,
        allow_unicode=True,
        blank=True,
    )

    sku = models.CharField(
        "رمز المنتج",
        max_length=100,
        unique=True,
        db_index=True,
    )

    short_description = models.CharField(
        "الوصف المختصر",
        max_length=350,
        blank=True,
    )

    description = models.TextField(
        "وصف المنتج",
    )

    price = models.DecimalField(
        "السعر",
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
    )

    compare_at_price = models.DecimalField(
        "السعر قبل الخصم",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
    )

    cost_price = models.DecimalField(
        "سعر التكلفة",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
    )

    stock = models.PositiveIntegerField(
        "الكمية المتاحة",
        default=0,
    )

    low_stock_threshold = models.PositiveIntegerField(
        "حد تنبيه المخزون",
        default=5,
    )

    track_stock = models.BooleanField(
        "تتبع المخزون",
        default=True,
    )

    main_image = CloudinaryField(
        "الصورة الرئيسية",
        resource_type="image",
        folder="cooffe99/products/main",
        blank=True,
        null=True,
    )

    weight = models.DecimalField(
        "الوزن بالكيلوغرام",
        max_digits=8,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                Decimal("0.000"),
            ),
        ],
    )

    country = models.CharField("الدولة", max_length=120, blank=True, db_index=True)
    region = models.CharField("المنطقة", max_length=150, blank=True, db_index=True)
    farm = models.CharField("المزرعة", max_length=180, blank=True)
    producer = models.CharField("المنتج أو المزارع", max_length=180, blank=True)
    variety = models.CharField("السلالة", max_length=180, blank=True, db_index=True)
    processing_method = models.CharField("طريقة المعالجة", max_length=30, choices=PROCESS_CHOICES, blank=True, db_index=True)
    altitude_masl = models.PositiveIntegerField("الارتفاع عن سطح البحر (م)", blank=True, null=True)
    roast_level = models.CharField("درجة التحميص", max_length=20, choices=ROAST_CHOICES, blank=True, db_index=True)
    flavor_notes = models.CharField("الإيحاءات والنكهات", max_length=350, blank=True)
    acidity = models.PositiveSmallIntegerField("الحموضة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    sweetness = models.PositiveSmallIntegerField("الحلاوة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    bitterness = models.PositiveSmallIntegerField("المرارة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    body = models.PositiveSmallIntegerField("القوام", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    roast_date = models.DateField("تاريخ التحميص", blank=True, null=True)
    roast_batch_number = models.CharField("رقم دفعة التحميص", max_length=100, blank=True, db_index=True)
    suitable_brew_methods = models.CharField("طرق التحضير المناسبة", max_length=350, blank=True)
    meta_title = models.CharField("عنوان SEO", max_length=200, blank=True)
    meta_description = models.CharField("وصف SEO", max_length=320, blank=True)
    is_published = models.BooleanField("منشور", default=True, db_index=True)

    is_active = models.BooleanField(
        "نشط",
        default=True,
    )

    is_featured = models.BooleanField(
        "منتج مميز",
        default=False,
    )

    is_digital = models.BooleanField(
        "منتج رقمي",
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
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["name"],
            ),
            models.Index(
                fields=["sku"],
            ),
            models.Index(
                fields=["is_active", "is_featured"],
            ),
            models.Index(
                fields=["category", "is_active"],
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=Q(
                    price__gte=0,
                ),
                name="product_price_gte_zero",
            ),
            models.CheckConstraint(
                condition=(
                    Q(compare_at_price__isnull=True)
                    | Q(compare_at_price__gte=0)
                ),
                name="product_compare_price_gte_zero",
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def is_in_stock(self):
        return (
            not self.track_stock
            or self.stock > 0
        )

    @property
    def discount_percentage(self):
        if (
            self.compare_at_price
            and self.compare_at_price > self.price
            and self.compare_at_price > 0
        ):
            discount = (
                (
                    self.compare_at_price
                    - self.price
                )
                / self.compare_at_price
            ) * Decimal("100")

            return round(
                discount,
                2,
            )

        return Decimal("0.00")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                self.name,
                allow_unicode=True,
            )

            slug = base_slug
            counter = 1

            while (
                Product.objects
                .filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def clean(self):
        if self.compare_at_price is not None and self.compare_at_price < self.price:
            raise ValidationError({"compare_at_price": "سعر المقارنة يجب ألا يقل عن السعر الحالي."})
        if self.altitude_masl is not None and self.altitude_masl > 5000:
            raise ValidationError({"altitude_masl": "الارتفاع يجب أن يكون بين 0 و5000 متر."})

    @property
    def price_per_100g(self):
        if not self.weight or self.weight <= 0:
            return None
        return (self.price / (self.weight * Decimal("10"))).quantize(Decimal("0.01"))


# =============================================================================
# صور المنتجات الإضافية
# =============================================================================


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="المنتج",
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = CloudinaryField(
        "الصورة",
        resource_type="image",
        folder="cooffe99/products/gallery",
    )

    alt_text = models.CharField(
        "النص البديل",
        max_length=200,
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        "ترتيب العرض",
        default=0,
    )

    created_at = models.DateTimeField(
        "تاريخ الإضافة",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "صورة منتج"
        verbose_name_plural = "صور المنتجات"
        ordering = ["display_order", "id"]

    def __str__(self):
        return f"صورة {self.product.name}"


# =============================================================================
# متغيرات المنتجات
# =============================================================================


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="المنتج",
        on_delete=models.CASCADE,
        related_name="variants",
    )

    name = models.CharField(
        "اسم المتغير",
        max_length=150,
        help_text="مثال: أحمر / 256 جيجابايت.",
    )

    sku = models.CharField(
        "رمز المتغير",
        max_length=100,
        unique=True,
        db_index=True,
    )

    price = models.DecimalField(
        "السعر",
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
        help_text="اتركه فارغًا لاستخدام سعر المنتج الأساسي.",
    )

    stock = models.PositiveIntegerField(
        "المخزون",
        default=0,
    )

    image = CloudinaryField(
        "صورة المتغير",
        resource_type="image",
        folder="cooffe99/products/variants",
        blank=True,
        null=True,
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
        verbose_name = "متغير منتج"
        verbose_name_plural = "متغيرات المنتجات"
        ordering = ["product", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "name"],
                name="unique_variant_name_per_product",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def effective_price(self):
        if self.price is not None:
            return self.price

        return self.product.price


# =============================================================================
# خصائص المنتجات
# =============================================================================


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="المنتج",
        on_delete=models.CASCADE,
        related_name="attributes",
    )

    name = models.CharField(
        "اسم الخاصية",
        max_length=150,
    )

    value = models.CharField(
        "قيمة الخاصية",
        max_length=250,
    )

    display_order = models.PositiveIntegerField(
        "ترتيب العرض",
        default=0,
    )

    class Meta:
        verbose_name = "خاصية منتج"
        verbose_name_plural = "خصائص المنتجات"
        ordering = ["display_order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "name"],
                name="unique_attribute_name_per_product",
            ),
        ]

    def __str__(self):
        return f"{self.name}: {self.value}"


# =============================================================================
# تقييمات المنتجات
# =============================================================================


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name="المنتج",
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )

    rating = models.PositiveSmallIntegerField(
        "التقييم",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    title = models.CharField(
        "عنوان التقييم",
        max_length=200,
        blank=True,
    )

    comment = models.TextField(
        "التعليق",
        blank=True,
    )
    quality_rating = models.PositiveSmallIntegerField("الجودة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    aroma_rating = models.PositiveSmallIntegerField("الرائحة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    sweetness_rating = models.PositiveSmallIntegerField("الحلاوة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    acidity_rating = models.PositiveSmallIntegerField("الحموضة", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    body_rating = models.PositiveSmallIntegerField("القوام", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    value_rating = models.PositiveSmallIntegerField("القيمة مقابل السعر", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    would_buy_again = models.BooleanField("سيشتريه مرة أخرى", default=False)
    is_verified_purchase = models.BooleanField("مشتري موثق", default=False, editable=False, db_index=True)

    is_approved = models.BooleanField(
        "معتمد",
        default=False,
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
        verbose_name = "تقييم منتج"
        verbose_name_plural = "تقييمات المنتجات"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_review_per_user_product",
            ),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"


class ReviewImage(models.Model):
    review = models.ForeignKey(ProductReview, verbose_name="المراجعة", on_delete=models.CASCADE, related_name="images")
    image = CloudinaryField("الصورة", resource_type="image", folder="cooffe99/reviews")
    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)

    class Meta:
        verbose_name = "صورة مراجعة"
        verbose_name_plural = "صور المراجعات"

    def __str__(self):
        return f"صورة مراجعة {self.review_id}"

