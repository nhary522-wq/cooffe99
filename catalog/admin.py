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

admin.site.register(ReviewImage)


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

    @admin.display(
        description="متوفر",
        boolean=True,
    )
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
