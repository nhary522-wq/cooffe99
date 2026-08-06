from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .models import Brand, Product, ProductVariant


safe_document_extensions = FileExtensionValidator(["pdf", "jpg", "jpeg", "png", "webp"])
def validate_document_size(value):
    if value.size > 8 * 1024 * 1024: raise ValidationError("حجم الملف يجب ألا يتجاوز 8 ميجابايت.")


class Supplier(models.Model):
    TYPES = [("manufacturer", "مصنع"), ("wholesaler", "تاجر جملة"), ("store", "متجر"), ("distributor", "موزع"), ("other", "أخرى")]
    name = models.CharField("اسم المورد", max_length=180, unique=True)
    supplier_type = models.CharField("النوع", max_length=20, choices=TYPES, default="other", db_index=True)
    slug = models.SlugField("الرابط المختصر", max_length=200, unique=True, allow_unicode=True)
    country = models.CharField("الدولة", max_length=120, blank=True, db_index=True)
    city = models.CharField("المدينة", max_length=120, blank=True)
    website = models.URLField("الموقع", blank=True)
    contact_name = models.CharField("جهة الاتصال", max_length=150, blank=True)
    email = models.EmailField("البريد", blank=True)
    phone = models.CharField("الهاتف", max_length=30, blank=True)
    minimum_order = models.DecimalField("الحد الأدنى للطلب", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    preparation_days = models.PositiveIntegerField("متوسط التجهيز بالأيام", default=0)
    shipping_days = models.PositiveIntegerField("متوسط الشحن بالأيام", default=0)
    currency = models.CharField("العملة", max_length=3, default="SAR")
    payment_terms = models.TextField("شروط الدفع", blank=True)
    return_policy = models.TextField("سياسة الإرجاع", blank=True)
    internal_rating = models.PositiveSmallIntegerField("التقييم الداخلي", default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_verified = models.BooleanField("موثق", default=False)
    admin_notes = models.TextField("ملاحظات الإدارة", blank=True)
    is_active = models.BooleanField("نشط", default=True, db_index=True)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    class Meta: app_label="catalog"; verbose_name="مورد"; verbose_name_plural="الموردون"; ordering=["name"]
    def __str__(self): return self.name


class Manufacturer(models.Model):
    name = models.CharField("اسم المصنع", max_length=180, unique=True)
    slug = models.SlugField("الرابط المختصر", max_length=200, unique=True, allow_unicode=True)
    country = models.CharField("بلد التصنيع", max_length=120, blank=True, db_index=True)
    brand_country = models.CharField("بلد العلامة", max_length=120, blank=True)
    brand = models.ForeignKey(Brand, verbose_name="العلامة", on_delete=models.SET_NULL, null=True, blank=True, related_name="manufacturers")
    website = models.URLField("الموقع", blank=True)
    description = models.TextField("الوصف", blank=True)
    is_active = models.BooleanField("نشط", default=True)
    class Meta: app_label="catalog"; verbose_name="مصنع"; verbose_name_plural="المصانع"
    def __str__(self): return self.name


class ProcessingMethod(models.Model):
    name = models.CharField("طريقة المعالجة", max_length=120, unique=True)
    slug = models.SlugField("الرابط المختصر", max_length=140, unique=True, allow_unicode=True)
    description = models.TextField("الوصف", blank=True)
    is_active = models.BooleanField("نشطة", default=True)
    class Meta: app_label="catalog"; verbose_name="طريقة معالجة"; verbose_name_plural="طرق المعالجة"
    def __str__(self): return self.name


class FlavorNote(models.Model):
    name = models.CharField("الإيحاء", max_length=100, unique=True)
    group = models.CharField("المجموعة", max_length=100, blank=True, db_index=True)
    class Meta: app_label="catalog"; verbose_name="إيحاء نكهة"; verbose_name_plural="إيحاءات النكهة"; ordering=["group", "name"]
    def __str__(self): return self.name


class CropProfile(models.Model):
    product = models.OneToOneField(Product, verbose_name="المحصول", on_delete=models.CASCADE, related_name="crop_profile")
    processing_method = models.ForeignKey(ProcessingMethod, verbose_name="المعالجة", on_delete=models.SET_NULL, null=True, blank=True, related_name="crops")
    processing_description = models.TextField("وصف المعالجة", blank=True)
    fermentation_hours = models.PositiveIntegerField("مدة التخمير بالساعات", null=True, blank=True)
    drying_method = models.CharField("طريقة التجفيف", max_length=150, blank=True)
    drying_days = models.PositiveIntegerField("مدة التجفيف بالأيام", null=True, blank=True)
    moisture_percentage = models.DecimalField("نسبة الرطوبة", max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    water_activity = models.DecimalField("النشاط المائي", max_digits=4, decimal_places=3, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(1)])
    processing_notes = models.TextField("ملاحظات المعالجة", blank=True)
    primary_notes = models.ManyToManyField(FlavorNote, verbose_name="الإيحاءات الرئيسية", blank=True, related_name="primary_crops")
    secondary_notes = models.ManyToManyField(FlavorNote, verbose_name="الإيحاءات الثانوية", blank=True, related_name="secondary_crops")
    quality_document = models.FileField("ملف الجودة", upload_to="products/quality/", blank=True, validators=[safe_document_extensions, validate_document_size])
    class Meta: app_label="catalog"; verbose_name="بطاقة محصول"; verbose_name_plural="بطاقات المحاصيل"
    def __str__(self): return str(self.product)


class RoastBatch(models.Model):
    STATUSES = [("planned", "مخططة"), ("resting", "فترة راحة"), ("available", "متاحة"), ("closed", "منتهية")]
    product = models.ForeignKey(Product, verbose_name="المحصول", on_delete=models.PROTECT, related_name="roast_batches")
    roastery = models.ForeignKey(Brand, verbose_name="المحمصة", on_delete=models.PROTECT, related_name="roast_batches")
    batch_number = models.CharField("رقم الدفعة", max_length=100)
    roast_date = models.DateField("تاريخ التحميص")
    roast_level = models.CharField("درجة التحميص", max_length=30)
    produced_quantity = models.DecimalField("الكمية المنتجة كجم", max_digits=10, decimal_places=3, validators=[MinValueValidator(0)])
    best_from_days = models.PositiveIntegerField("بدء الاستخدام بعد أيام", default=7)
    best_until_days = models.PositiveIntegerField("أفضل فترة حتى أيام", default=35)
    expiry_date = models.DateField("تاريخ الانتهاء", null=True, blank=True)
    roaster_notes = models.TextField("ملاحظات المحمص", blank=True)
    status = models.CharField("الحالة", max_length=15, choices=STATUSES, default="planned", db_index=True)
    quality_results = models.TextField("نتائج الجودة", blank=True)
    variant = models.ForeignKey(ProductVariant, verbose_name="مخزون الخيار", on_delete=models.SET_NULL, null=True, blank=True, related_name="roast_batches")
    class Meta:
        app_label="catalog"; verbose_name="دفعة تحميص"; verbose_name_plural="دفعات التحميص"; ordering=["-roast_date"]
        constraints=[models.UniqueConstraint(fields=["roastery", "batch_number"], name="unique_roastery_roast_batch")]
        indexes=[models.Index(fields=["product", "roast_date"], name="roast_product_date_idx")]
    def __str__(self): return f"{self.product} - {self.batch_number}"
    @property
    def freshness_status(self):
        age=(timezone.localdate()-self.roast_date).days
        if age < self.best_from_days: return "يحتاج إلى فترة راحة"
        if age <= self.best_until_days: return "في أفضل فترة استخدام" if age > 10 else "حديث التحميص"
        if age <= self.best_until_days + 10: return "يقترب من نهاية فترة النضارة"
        return "تجاوز الفترة المقترحة"


class GrindOption(models.Model):
    name=models.CharField("خيار الطحن", max_length=120, unique=True)
    slug=models.SlugField("الرابط المختصر", max_length=140, unique=True)
    freshness_notice=models.CharField("تنبيه النضارة", max_length=250, default="البن المطحون قد يفقد جزءًا من نضارته أسرع من الحبوب الكاملة.")
    is_active=models.BooleanField("نشط", default=True)
    class Meta: app_label="catalog"; verbose_name="خيار طحن"; verbose_name_plural="خيارات الطحن"
    def __str__(self): return self.name


class ProductGrindOption(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="grind_options", verbose_name="المحصول")
    option=models.ForeignKey(GrindOption, on_delete=models.PROTECT, related_name="products", verbose_name="الخيار")
    is_default=models.BooleanField("افتراضي", default=False)
    class Meta:
        app_label="catalog"; verbose_name="طحن محصول"; verbose_name_plural="طحن المحاصيل"
        constraints=[models.UniqueConstraint(fields=["product", "option"], name="unique_product_grind_option")]


class ProductBrewRecipe(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="brew_recipes", verbose_name="المنتج")
    brew_method=models.ForeignKey("core.BrewMethod", on_delete=models.CASCADE, related_name="product_recipes", verbose_name="طريقة التحضير")
    grind_size=models.CharField("درجة الطحن", max_length=100)
    coffee_grams=models.DecimalField("كمية البن", max_digits=6, decimal_places=2, validators=[MinValueValidator(0.1)])
    water_ml=models.PositiveIntegerField("كمية الماء")
    water_temperature=models.PositiveIntegerField("حرارة الماء")
    extraction_seconds=models.PositiveIntegerField("وقت الاستخلاص")
    difficulty=models.CharField("الصعوبة", max_length=30, blank=True)
    short_recipe=models.TextField("وصفة مختصرة")
    roastery_notes=models.TextField("ملاحظات المحمصة", blank=True)
    class Meta:
        app_label="catalog"; verbose_name="وصفة محصول"; verbose_name_plural="وصفات المحاصيل"
        constraints=[models.UniqueConstraint(fields=["product", "brew_method"], name="unique_product_brew_recipe")]


class ProductJourneyStage(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="journey_stages", verbose_name="المحصول")
    title=models.CharField("العنوان", max_length=150)
    description=models.TextField("الوصف")
    event_date=models.DateField("التاريخ", null=True, blank=True)
    location=models.CharField("الموقع", max_length=180, blank=True)
    image=models.ImageField("الصورة", upload_to="products/journey/", blank=True)
    display_order=models.PositiveIntegerField("الترتيب", default=0)
    class Meta: app_label="catalog"; verbose_name="مرحلة رحلة"; verbose_name_plural="رحلة المحصول"; ordering=["display_order", "id"]


class ToolProfile(models.Model):
    product=models.OneToOneField(Product, on_delete=models.CASCADE, related_name="tool_profile", verbose_name="الأداة")
    manufacturer=models.ForeignKey(Manufacturer, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="المصنع")
    supplier=models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="المورد")
    supplier_number=models.CharField("رقم المورد", max_length=100, blank=True)
    material=models.CharField("المادة", max_length=120, blank=True, db_index=True)
    color=models.CharField("اللون", max_length=100, blank=True, db_index=True)
    dimensions=models.CharField("الأبعاد", max_length=150, blank=True)
    capacity=models.CharField("السعة", max_length=100, blank=True, db_index=True)
    heat_resistance=models.CharField("مقاومة الحرارة", max_length=100, blank=True)
    impact_resistant=models.BooleanField("مقاوم للصدمات", default=False)
    water_resistant=models.BooleanField("مقاوم للماء", default=False)
    bpa_free=models.BooleanField("خال من BPA", default=False)
    dishwasher_safe=models.BooleanField("مناسب لغسالة الصحون", default=False)
    microwave_safe=models.BooleanField("مناسب للميكروويف", default=False)
    certifications=models.TextField("الشهادات", blank=True)
    warranty_months=models.PositiveIntegerField("مدة الضمان بالأشهر", default=0)
    video_url=models.URLField("فيديو الاستخدام", blank=True)
    class Meta: app_label="catalog"; verbose_name="ملف أداة"; verbose_name_plural="ملفات الأدوات"


class ToolSpecification(models.Model):
    DATA_TYPES=[("text","نص"),("number","رقم"),("boolean","نعم/لا")]
    name=models.CharField("اسم المواصفة", max_length=120)
    slug=models.SlugField("المعرف", max_length=140, unique=True)
    category=models.ForeignKey("catalog.Category", on_delete=models.SET_NULL, null=True, blank=True, related_name="tool_specifications", verbose_name="التصنيف")
    data_type=models.CharField("نوع القيمة", max_length=10, choices=DATA_TYPES, default="text")
    unit=models.CharField("الوحدة", max_length=30, blank=True)
    is_filterable=models.BooleanField("قابلة للتصفية", default=False, db_index=True)
    class Meta: app_label="catalog"; verbose_name="مواصفة أداة"; verbose_name_plural="مواصفات الأدوات"
    def __str__(self): return self.name


class ToolSpecificationValue(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="tool_spec_values", verbose_name="الأداة")
    specification=models.ForeignKey(ToolSpecification, on_delete=models.PROTECT, related_name="values", verbose_name="المواصفة")
    value=models.CharField("القيمة", max_length=250, db_index=True)
    class Meta:
        app_label="catalog"; verbose_name="قيمة مواصفة"; verbose_name_plural="قيم المواصفات"
        constraints=[models.UniqueConstraint(fields=["product","specification"], name="unique_tool_spec_value")]


class VariantCommercialData(models.Model):
    variant=models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name="commercial", verbose_name="الخيار")
    supplier=models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="variants", verbose_name="المورد")
    barcode=models.CharField("الباركود", max_length=100, blank=True, db_index=True)
    weight_grams=models.PositiveIntegerField("الوزن بالجرام", null=True, blank=True)
    compare_at_price=models.DecimalField("سعر المقارنة", max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    purchase_cost=models.DecimalField("تكلفة الشراء", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    shipping_cost=models.DecimalField("الشحن", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    customs_cost=models.DecimalField("الجمارك", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    tax_cost=models.DecimalField("الضرائب", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    storage_cost=models.DecimalField("التخزين", max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    reserved_stock=models.PositiveIntegerField("المحجوز", default=0)
    low_stock_threshold=models.PositiveIntegerField("حد إعادة الطلب", default=5)
    preorder_allowed=models.BooleanField("طلب مسبق", default=False)
    max_per_order=models.PositiveIntegerField("أقصى كمية", default=20)
    dimensions=models.CharField("الأبعاد", max_length=150, blank=True)
    currency=models.CharField("العملة", max_length=3, default="SAR")
    lead_time_days=models.PositiveIntegerField("مدة التجهيز", default=0)
    supplier_url=models.URLField("رابط المورد الداخلي", blank=True)
    class Meta:
        app_label="catalog"; verbose_name="بيانات تجارية للخيار"; verbose_name_plural="البيانات التجارية للخيارات"
        permissions=[("view_product_costs", "يمكنه عرض تكاليف المنتجات وهوامش الربح")]
    @property
    def available_stock(self): return max(self.variant.stock-self.reserved_stock,0)
    @property
    def final_cost(self): return sum((self.purchase_cost,self.shipping_cost,self.customs_cost,self.tax_cost,self.storage_cost),Decimal("0"))
    @property
    def profit_margin(self):
        price=self.variant.effective_price
        return (((price-self.final_cost)/price)*100).quantize(Decimal("0.01")) if price else Decimal("0")
    @property
    def price_per_100g(self): return ((self.variant.effective_price/Decimal(self.weight_grams))*100).quantize(Decimal("0.01")) if self.weight_grams else None
    @property
    def price_per_kg(self): return ((self.variant.effective_price/Decimal(self.weight_grams))*1000).quantize(Decimal("0.01")) if self.weight_grams else None
    @property
    def estimated_cups(self): return self.weight_grams//15 if self.weight_grams else None


class QualityInspection(models.Model):
    STATUSES=[("pending","قيد الفحص"),("approved","معتمد"),("rejected","مرفوض")]
    receipt_batch=models.CharField("دفعة الاستلام", max_length=100, unique=True)
    supplier=models.ForeignKey(Supplier,on_delete=models.PROTECT,related_name="inspections",verbose_name="المورد")
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="quality_inspections",verbose_name="الأداة")
    received_at=models.DateField("تاريخ الاستلام")
    received_quantity=models.PositiveIntegerField("المستلم")
    accepted_quantity=models.PositiveIntegerField("المقبول",default=0)
    rejected_quantity=models.PositiveIntegerField("المرفوض",default=0)
    rejection_reason=models.TextField("سبب الرفض",blank=True)
    packaging_quality=models.PositiveSmallIntegerField("جودة التغليف",default=3,validators=[MinValueValidator(1),MaxValueValidator(5)])
    manufacturing_quality=models.PositiveSmallIntegerField("جودة التصنيع",default=3,validators=[MinValueValidator(1),MaxValueValidator(5)])
    operation_test=models.BooleanField("اختبار التشغيل",default=False)
    safety_test=models.BooleanField("اختبار السلامة",default=False)
    inspector_notes=models.TextField("ملاحظات المفتش",blank=True)
    status=models.CharField("الاعتماد",max_length=12,choices=STATUSES,default="pending",db_index=True)
    class Meta: app_label="catalog"; verbose_name="فحص جودة"; verbose_name_plural="فحوص الجودة"
    def clean(self):
        if self.accepted_quantity+self.rejected_quantity>self.received_quantity: raise ValidationError("مجموع المقبول والمرفوض يتجاوز الكمية المستلمة.")


class ProductCompatibility(models.Model):
    TYPES=[("compatible","متوافق"),("partial","متوافق جزئيًا"),("adapter","يحتاج محول"),("incompatible","غير متوافق"),("alternative","بديل"),("spare","قطعة غيار"),("accessory","ملحق")]
    source=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="compatibilities_from",verbose_name="المنتج")
    target=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="compatibilities_to",verbose_name="المنتج المرتبط")
    relation_type=models.CharField("نوع العلاقة",max_length=15,choices=TYPES,db_index=True)
    reason=models.TextField("السبب")
    class Meta:
        app_label="catalog"; verbose_name="توافق منتج"; verbose_name_plural="توافق المنتجات"
        constraints=[models.UniqueConstraint(fields=["source","target"],name="unique_product_compatibility"),models.CheckConstraint(condition=~models.Q(source=models.F("target")),name="compatibility_not_self")]


class ToolBundle(models.Model):
    name=models.CharField("اسم الباقة",max_length=180)
    slug=models.SlugField("الرابط المختصر",max_length=200,unique=True)
    bundle_price=models.DecimalField("سعر الباقة",max_digits=12,decimal_places=2,validators=[MinValueValidator(0)])
    image=models.ImageField("الصورة",upload_to="products/bundles/",blank=True)
    is_active=models.BooleanField("نشطة",default=True,db_index=True)
    class Meta: app_label="catalog"; verbose_name="باقة أدوات"; verbose_name_plural="باقات الأدوات"
    def __str__(self): return self.name
    @property
    def original_price(self): return sum((item.product.price*item.quantity for item in self.items.select_related("product")),Decimal("0"))
    @property
    def savings(self): return max(self.original_price-self.bundle_price,Decimal("0"))
    @property
    def available_stock(self): return min((item.product.stock//item.quantity for item in self.items.select_related("product") if item.is_required),default=0)


class ToolBundleItem(models.Model):
    bundle=models.ForeignKey(ToolBundle,on_delete=models.CASCADE,related_name="items",verbose_name="الباقة")
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name="bundle_items",verbose_name="المنتج")
    quantity=models.PositiveIntegerField("الكمية",default=1,validators=[MinValueValidator(1)])
    is_required=models.BooleanField("مكون أساسي",default=True)
    class Meta:
        app_label="catalog"; verbose_name="عنصر باقة"; verbose_name_plural="عناصر الباقات"
        constraints=[models.UniqueConstraint(fields=["bundle","product"],name="unique_bundle_product")]


class InventoryMovement(models.Model):
    TYPES=[("in","إضافة"),("reserve","حجز"),("release","إلغاء حجز"),("out","صرف"),("damage","تالف"),("return","مرتجع"),("count","جرد")]
    variant=models.ForeignKey(ProductVariant,on_delete=models.PROTECT,related_name="inventory_movements",verbose_name="الخيار")
    movement_type=models.CharField("نوع الحركة",max_length=12,choices=TYPES,db_index=True)
    quantity=models.PositiveIntegerField("الكمية",validators=[MinValueValidator(1)])
    reference=models.CharField("المرجع",max_length=150,blank=True)
    warehouse=models.CharField("المستودع",max_length=120,blank=True)
    notes=models.TextField("ملاحظات",blank=True)
    created_at=models.DateTimeField("تاريخ الحركة",auto_now_add=True)
    class Meta: app_label="catalog"; verbose_name="حركة مخزون"; verbose_name_plural="حركات المخزون"; ordering=["-created_at"]
