from django.contrib import admin

from .models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductImage,
    ProductReview,
    ProductVariant,
    ReviewImage,
)
from .domain_models import (CropProfile, FlavorNote, GrindOption, InventoryMovement,
    Manufacturer, ProcessingMethod, ProductBrewRecipe, ProductCompatibility,
    ProductGrindOption, ProductJourneyStage, QualityInspection, RoastBatch,
    Supplier, ToolBundle, ToolBundleItem, ToolProfile, ToolSpecification,
    ToolSpecificationValue, VariantCommercialData)

admin.site.register(ReviewImage)


class ProductGrindInline(admin.TabularInline): model=ProductGrindOption; extra=0
class ProductRecipeInline(admin.TabularInline): model=ProductBrewRecipe; extra=0
class ProductJourneyInline(admin.TabularInline): model=ProductJourneyStage; extra=0
class ToolSpecValueInline(admin.TabularInline): model=ToolSpecificationValue; extra=0
class BundleItemInline(admin.TabularInline): model=ToolBundleItem; extra=1

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display=("name","supplier_type","country","internal_rating","is_verified","is_active")
    list_filter=("supplier_type","country","is_verified","is_active")
    search_fields=("name","contact_name","email","phone")
    prepopulated_fields={"slug":("name",)}

@admin.register(RoastBatch)
class RoastBatchAdmin(admin.ModelAdmin):
    list_display=("batch_number","product","roastery","roast_date","freshness_status","status")
    list_filter=("status","roast_level","roastery")
    search_fields=("batch_number","product__name")
    list_select_related=("product","roastery","variant")

@admin.register(VariantCommercialData)
class VariantCommercialDataAdmin(admin.ModelAdmin):
    list_display=("variant","supplier","available_stock","final_cost","profit_margin")
    list_select_related=("variant","variant__product","supplier")
    def get_exclude(self, request, obj=None):
        if request.user.has_perm("catalog.view_product_costs"): return ()
        return ("purchase_cost","shipping_cost","customs_cost","tax_cost","storage_cost","supplier_url")

@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display=("receipt_batch","product","supplier","received_quantity","accepted_quantity","rejected_quantity","status")
    list_filter=("status","supplier")
    list_select_related=("product","supplier")

@admin.register(ToolBundle)
class ToolBundleAdmin(admin.ModelAdmin):
    list_display=("name","bundle_price","original_price","savings","available_stock","is_active")
    prepopulated_fields={"slug":("name",)}
    inlines=(BundleItemInline,)

admin.site.register([Manufacturer, ProcessingMethod, FlavorNote, CropProfile,
    GrindOption, ProductGrindOption, ProductBrewRecipe, ProductJourneyStage,
    ToolProfile, ToolSpecification, ToolSpecificationValue, ProductCompatibility,
    ToolBundleItem, InventoryMovement])


class ProductImageInline(admin.TabularInline):
    model = ProductImage

    extra = 1

    fields = (
        "image",
        "alt_text",
        "display_order",
    )

    ordering = (
        "display_order",
    )


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant

    extra = 0

    fields = (
        "name",
        "sku",
        "price",
        "stock",
        "image",
        "is_active",
    )

    show_change_link = True


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute

    extra = 1

    fields = (
        "name",
        "value",
        "display_order",
    )

    ordering = (
        "display_order",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "parent",
        "display_order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "parent",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    autocomplete_fields = (
        "parent",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "display_order",
        "name",
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website_url",
        "is_active",
        "created_at",
    )

    list_editable = (
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "website_url",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "name",
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "brand",
        "price",
        "stock",
        "is_in_stock_display",
        "is_active",
        "is_featured",
        "created_at",
    )

    list_editable = (
        "price",
        "stock",
        "is_active",
        "is_featured",
    )

    list_filter = (
        "is_active",
        "is_featured",
        "is_digital",
        "track_stock",
        "category",
        "brand",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "slug",
        "sku",
        "short_description",
        "description",
        "category__name",
        "brand__name",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    autocomplete_fields = (
        "category",
        "brand",
    )

    readonly_fields = (
        "discount_percentage",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "category",
        "brand",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    inlines = (
        ProductImageInline,
        ProductVariantInline,
        ProductAttributeInline,
        ProductGrindInline,
        ProductRecipeInline,
        ProductJourneyInline,
        ToolSpecValueInline,
    )

    fieldsets = (
        (
            "المعلومات الأساسية",
            {
                "fields": (
                    "category",
                    "brand",
                    "name",
                    "slug",
                    "sku",
                    "short_description",
                    "description",
                    "main_image",
                )
            },
        ),
        (
            "الأسعار",
            {
                "fields": (
                    "price",
                    "compare_at_price",
                    "cost_price",
                    "discount_percentage",
                )
            },
        ),
        (
            "المخزون والشحن",
            {
                "fields": (
                    "stock",
                    "low_stock_threshold",
                    "track_stock",
                    "weight",
                    "is_digital",
                )
            },
        ),
        (
            "حالة المنتج",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                )
            },
        ),
        (
            "التواريخ",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        return super().get_fieldsets(request, obj) + (
            ("بيانات الكتالوج", {"fields": ("product_type", "commercial_name", "display_order", "is_published", "meta_title", "meta_description")}),
            ("المنشأ والزراعة", {"classes": ("collapse",), "fields": ("country", "region", "village", "farm", "producer", "farm_story", "coffee_species", "variety", "altitude_min", "altitude_max", "soil_type", "irrigation_method", "harvest_season", "harvest_date", "harvest_method", "latitude", "longitude", "origin_certificate", "certifications")}),
            ("الجودة والتذوق", {"classes": ("collapse",), "fields": ("sca_score", "bean_density", "bean_size", "defect_count", "quality_grade", "evaluator_name", "evaluation_date", "quality_results", "flavor_notes", "secondary_flavor_notes", "aroma", "acidity", "sweetness", "bitterness", "body", "balance", "complexity", "cleanliness", "finish", "mouthfeel")}),
            ("بيانات الأدوات", {"classes": ("collapse",), "fields": ("country_of_manufacture", "model_number", "release_year", "usage_level", "warranty", "box_contents", "usage_instructions", "setup_steps", "safety_warnings", "cleaning_instructions", "maintenance_schedule", "common_issues", "manual_file")}),
            ("الوسائط", {"classes": ("collapse",), "fields": ("packaging_image", "farm_image", "roast_image", "video_url")}),
        )

    @admin.display(description="متوفر", boolean=True)
    def is_in_stock_display(self, obj):
        return obj.is_in_stock


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "alt_text",
        "display_order",
        "created_at",
    )

    list_editable = (
        "display_order",
    )

    list_filter = (
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "alt_text",
    )

    autocomplete_fields = (
        "product",
    )

    readonly_fields = (
        "created_at",
    )

    list_select_related = (
        "product",
    )

    ordering = (
        "display_order",
        "id",
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "product",
        "sku",
        "price",
        "effective_price_display",
        "stock",
        "is_active",
        "created_at",
    )

    list_editable = (
        "price",
        "stock",
        "is_active",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "sku",
        "product__name",
        "product__sku",
    )

    autocomplete_fields = (
        "product",
    )

    readonly_fields = (
        "effective_price_display",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "product",
    )

    @admin.display(description="السعر الفعلي")
    def effective_price_display(self, obj):
        return obj.effective_price


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "value",
        "display_order",
    )

    list_editable = (
        "display_order",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "name",
        "value",
    )

    autocomplete_fields = (
        "product",
    )

    list_select_related = (
        "product",
    )

    ordering = (
        "display_order",
        "name",
    )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "user",
        "rating",
        "title",
        "is_approved",
        "created_at",
    )

    list_editable = (
        "is_approved",
    )

    list_filter = (
        "rating",
        "is_approved",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "user__username",
        "user__email",
        "title",
        "comment",
    )

    autocomplete_fields = (
        "product",
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "product",
        "user",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )
