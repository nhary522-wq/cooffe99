from django.conf import settings
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


class BrewTool(models.Model):
    name = models.CharField("اسم الأداة", max_length=120, unique=True)
    slug = models.SlugField("الرابط المختصر", max_length=140, unique=True, allow_unicode=True)
    is_active = models.BooleanField("نشطة", default=True)

    class Meta:
        verbose_name = "أداة تحضير"
        verbose_name_plural = "أدوات التحضير"
        ordering = ["name"]

    def __str__(self): return self.name


class BrewMethod(models.Model):
    DIFFICULTY = [("easy", "سهل"), ("medium", "متوسط"), ("advanced", "متقدم")]
    name = models.CharField("الاسم", max_length=150)
    slug = models.SlugField("الرابط المختصر", max_length=170, unique=True, allow_unicode=True)
    short_description = models.CharField("وصف مختصر", max_length=350)
    description = models.TextField("وصف تفصيلي")
    image = models.ImageField("الصورة الرئيسية", upload_to="brew/methods/", blank=True)
    difficulty = models.CharField("مستوى الصعوبة", max_length=20, choices=DIFFICULTY, db_index=True)
    duration_minutes = models.PositiveIntegerField("الوقت المتوقع بالدقائق", validators=[MinValueValidator(1)])
    coffee_grams = models.DecimalField("كمية البن (جرام)", max_digits=7, decimal_places=2, validators=[MinValueValidator(1)])
    water_ml = models.PositiveIntegerField("كمية الماء (مل)", validators=[MinValueValidator(1)])
    ratio = models.CharField("نسبة البن إلى الماء", max_length=30)
    grind_size = models.CharField("درجة الطحن", max_length=120)
    water_temperature = models.PositiveSmallIntegerField("درجة حرارة الماء", validators=[MinValueValidator(1)])
    tools = models.ManyToManyField(BrewTool, verbose_name="الأدوات المطلوبة", related_name="brew_methods", blank=True)
    common_mistakes = models.TextField("أخطاء شائعة", blank=True)
    tips = models.TextField("نصائح تحسين النتيجة", blank=True)
    products = models.ManyToManyField("catalog.Product", verbose_name="المنتجات المناسبة", related_name="brew_methods", blank=True)
    video_url = models.URLField("رابط فيديو اختياري", blank=True)
    is_published = models.BooleanField("منشورة", default=False, db_index=True)
    display_order = models.PositiveIntegerField("ترتيب الظهور", default=0)
    meta_title = models.CharField("عنوان SEO", max_length=200, blank=True)
    meta_description = models.CharField("وصف SEO", max_length=320, blank=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "طريقة تحضير"
        verbose_name_plural = "طرق التحضير"
        ordering = ["display_order", "name"]
        indexes = [models.Index(fields=["is_published", "difficulty", "display_order"], name="brew_publish_filter_idx")]

    def __str__(self): return self.name


class BrewStep(models.Model):
    method = models.ForeignKey(BrewMethod, verbose_name="طريقة التحضير", on_delete=models.CASCADE, related_name="steps")
    order = models.PositiveIntegerField("الترتيب")
    title = models.CharField("عنوان الخطوة", max_length=180)
    description = models.TextField("شرح الخطوة")
    duration_seconds = models.PositiveIntegerField("المدة بالثواني", blank=True, null=True)

    class Meta:
        verbose_name = "خطوة تحضير"
        verbose_name_plural = "خطوات التحضير"
        ordering = ["order", "id"]
        constraints = [models.UniqueConstraint(fields=["method", "order"], name="unique_brew_step_order")]

    def __str__(self): return f"{self.method} - {self.order}"


class ContentCategory(models.Model):
    CONTENT_TYPES = [("encyclopedia", "الموسوعة"), ("academy", "الأكاديمية"), ("term", "المصطلحات")]
    name = models.CharField("اسم التصنيف", max_length=150)
    slug = models.SlugField("الرابط المختصر", max_length=170, unique=True, allow_unicode=True)
    content_type = models.CharField("نوع المحتوى", max_length=20, choices=CONTENT_TYPES, db_index=True)
    description = models.TextField("الوصف", blank=True)
    display_order = models.PositiveIntegerField("الترتيب", default=0)

    class Meta:
        verbose_name = "تصنيف معرفي"
        verbose_name_plural = "تصنيفات الموسوعة والأكاديمية"
        ordering = ["content_type", "display_order", "name"]

    def __str__(self): return self.name


class CoffeeContent(models.Model):
    DIFFICULTY = [("beginner", "مبتدئ"), ("intermediate", "متوسط"), ("advanced", "متقدم")]
    category = models.ForeignKey(ContentCategory, verbose_name="التصنيف", on_delete=models.PROTECT, related_name="contents")
    title = models.CharField("العنوان", max_length=220)
    slug = models.SlugField("الرابط المختصر", max_length=250, unique=True, allow_unicode=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="الكاتب", on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.CharField("الملخص", max_length=400)
    content = models.TextField("المحتوى")
    image = models.ImageField("الصورة الرئيسية", upload_to="content/", blank=True)
    difficulty = models.CharField("المستوى", max_length=20, choices=DIFFICULTY, default="beginner", db_index=True)
    duration_minutes = models.PositiveIntegerField("مدة القراءة أو التعلم", default=5)
    display_order = models.PositiveIntegerField("ترتيب الظهور", default=0)
    is_published = models.BooleanField("منشور", default=False, db_index=True)
    published_at = models.DateTimeField("تاريخ النشر", blank=True, null=True)
    related_contents = models.ManyToManyField("self", verbose_name="محتوى مرتبط", symmetrical=True, blank=True)
    products = models.ManyToManyField("catalog.Product", verbose_name="منتجات مرتبطة", related_name="coffee_contents", blank=True)
    meta_title = models.CharField("عنوان SEO", max_length=200, blank=True)
    meta_description = models.CharField("وصف SEO", max_length=320, blank=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "مقال أو درس"
        verbose_name_plural = "الموسوعة والأكاديمية"
        ordering = ["display_order", "-published_at", "title"]
        indexes = [models.Index(fields=["is_published", "published_at"], name="content_publish_date_idx")]

    def __str__(self): return self.title
