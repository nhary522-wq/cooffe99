from django.contrib import admin

from .models import (Banner, BrewMethod, BrewStep, BrewTool, CoffeeContent,
                     ContactMessage, ContentCategory, SiteSetting, StaticPage)


class BrewStepInline(admin.TabularInline):
    model = BrewStep
    extra = 1


@admin.register(BrewMethod)
class BrewMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "difficulty", "duration_minutes", "is_published", "display_order")
    list_filter = ("difficulty", "is_published", "tools")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("tools", "products")
    inlines = (BrewStepInline,)


@admin.register(CoffeeContent)
class CoffeeContentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "difficulty", "is_published", "published_at")
    list_filter = ("category", "difficulty", "is_published")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related_contents", "products")


admin.site.register(BrewTool)
admin.site.register(ContentCategory)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = (
        "site_name",
        "email",
        "phone",
        "currency",
        "tax_percentage",
        "is_maintenance_mode",
        "updated_at",
    )

    list_filter = (
        "is_maintenance_mode",
        "currency",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "site_name",
        "site_description",
        "email",
        "phone",
        "whatsapp",
        "address",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "المعلومات الأساسية",
            {
                "fields": (
                    "site_name",
                    "site_description",
                    "logo",
                    "favicon",
                )
            },
        ),
        (
            "بيانات التواصل",
            {
                "fields": (
                    "email",
                    "phone",
                    "whatsapp",
                    "address",
                )
            },
        ),
        (
            "إعدادات المتجر",
            {
                "fields": (
                    "currency",
                    "tax_percentage",
                    "is_maintenance_mode",
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


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_order",
        "is_active",
        "starts_at",
        "ends_at",
        "created_at",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    list_filter = (
        "is_active",
        "starts_at",
        "ends_at",
        "created_at",
    )

    search_fields = (
        "title",
        "subtitle",
        "button_text",
        "button_url",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "display_order",
        "-created_at",
    )


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "is_active",
        "updated_at",
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
        "title",
        "slug",
        "content",
        "meta_description",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "subject",
        "is_read",
        "replied_at",
        "created_at",
    )

    list_editable = (
        "is_read",
    )

    list_filter = (
        "is_read",
        "replied_at",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
    )

    readonly_fields = (
        "name",
        "email",
        "phone",
        "subject",
        "message",
        "created_at",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )
