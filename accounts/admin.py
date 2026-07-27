from django.contrib import admin

from .models import Address, Profile, Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    autocomplete_fields = ["product"]

    fields = [
        "product",
        "created_at",
    ]

    readonly_fields = [
        "created_at",
    ]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "phone",
        "is_phone_verified",
        "marketing_consent",
        "created_at",
    ]

    list_filter = [
        "is_phone_verified",
        "marketing_consent",
        "created_at",
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "phone",
    ]

    autocomplete_fields = [
        "user",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    fieldsets = [
        (
            "بيانات المستخدم",
            {
                "fields": [
                    "user",
                    "avatar",
                    "phone",
                    "date_of_birth",
                ],
            },
        ),
        (
            "التوثيق والموافقات",
            {
                "fields": [
                    "is_phone_verified",
                    "marketing_consent",
                ],
            },
        ),
        (
            "التواريخ",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
            },
        ),
    ]

    ordering = [
        "-created_at",
    ]

    list_select_related = [
        "user",
    ]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        "recipient_name",
        "user",
        "address_type",
        "city",
        "district",
        "phone",
        "is_default",
        "created_at",
    ]

    list_filter = [
        "address_type",
        "country",
        "city",
        "is_default",
        "created_at",
    ]

    search_fields = [
        "recipient_name",
        "phone",
        "city",
        "district",
        "street",
        "building_number",
        "postal_code",
        "user__username",
        "user__email",
    ]

    autocomplete_fields = [
        "user",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]

    fieldsets = [
        (
            "بيانات المستخدم والمستلم",
            {
                "fields": [
                    "user",
                    "address_type",
                    "recipient_name",
                    "phone",
                ],
            },
        ),
        (
            "تفاصيل العنوان",
            {
                "fields": [
                    "country",
                    "city",
                    "district",
                    "street",
                    "building_number",
                    "postal_code",
                    "additional_number",
                ],
            },
        ),
        (
            "إعدادات إضافية",
            {
                "fields": [
                    "notes",
                    "is_default",
                ],
            },
        ),
        (
            "التواريخ",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                ],
            },
        ),
    ]

    ordering = [
        "-is_default",
        "-created_at",
    ]

    date_hierarchy = "created_at"

    list_select_related = [
        "user",
    ]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "products_count",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    autocomplete_fields = [
        "user",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "products_count",
    ]

    inlines = [
        WishlistItemInline,
    ]

    ordering = [
        "-created_at",
    ]

    list_select_related = [
        "user",
    ]

    @admin.display(description="عدد المنتجات")
    def products_count(self, obj):
        return obj.items.count()


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = [
        "product",
        "wishlist",
        "wishlist_user",
        "created_at",
    ]

    list_filter = [
        "created_at",
    ]

    search_fields = [
        "product__name",
        "wishlist__user__username",
        "wishlist__user__email",
    ]

    autocomplete_fields = [
        "wishlist",
        "product",
    ]

    readonly_fields = [
        "created_at",
    ]

    ordering = [
        "-created_at",
    ]

    list_select_related = [
        "wishlist",
        "wishlist__user",
        "product",
    ]

    @admin.display(description="المستخدم")
    def wishlist_user(self, obj):
        return obj.wishlist.user