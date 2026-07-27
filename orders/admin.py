from django.contrib import admin

from .models import Cart, CartItem, Coupon, Order, OrderItem, Shipment


class CartItemInline(admin.TabularInline):
    model = CartItem

    extra = 0

    autocomplete_fields = (
        "product",
        "variant",
    )

    readonly_fields = (
        "unit_price_display",
        "total_price_display",
        "created_at",
        "updated_at",
    )

    fields = (
        "product",
        "variant",
        "quantity",
        "unit_price_display",
        "total_price_display",
        "created_at",
        "updated_at",
    )

    @admin.display(description="سعر الوحدة")
    def unit_price_display(self, obj):
        if not obj.pk:
            return "-"

        return obj.unit_price

    @admin.display(description="الإجمالي")
    def total_price_display(self, obj):
        if not obj.pk:
            return "-"

        return obj.total_price


class OrderItemInline(admin.TabularInline):
    model = OrderItem

    extra = 0

    autocomplete_fields = (
        "product",
        "variant",
    )

    readonly_fields = (
        "total_price",
    )

    fields = (
        "product",
        "variant",
        "product_name",
        "variant_name",
        "sku",
        "unit_price",
        "quantity",
        "total_price",
    )


class ShipmentInline(admin.StackedInline):
    model = Shipment

    extra = 0

    max_num = 1

    fields = (
        "shipping_company",
        "tracking_number",
        "tracking_url",
        "status",
        "shipped_at",
        "delivered_at",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "items_count",
        "subtotal_display",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "session_key",
    )

    autocomplete_fields = (
        "user",
    )

    readonly_fields = (
        "subtotal_display",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
    )

    inlines = (
        CartItemInline,
    )

    @admin.display(description="عدد العناصر")
    def items_count(self, obj):
        return obj.items.count()

    @admin.display(description="إجمالي السلة")
    def subtotal_display(self, obj):
        return obj.subtotal


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "variant",
        "quantity",
        "unit_price_display",
        "total_price_display",
        "created_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "cart__user__username",
        "cart__session_key",
        "product__name",
        "product__sku",
        "variant__name",
        "variant__sku",
    )

    autocomplete_fields = (
        "cart",
        "product",
        "variant",
    )

    readonly_fields = (
        "unit_price_display",
        "total_price_display",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "cart",
        "product",
        "variant",
    )

    @admin.display(description="سعر الوحدة")
    def unit_price_display(self, obj):
        return obj.unit_price

    @admin.display(description="الإجمالي")
    def total_price_display(self, obj):
        return obj.total_price


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "minimum_order_amount",
        "usage_limit",
        "used_count",
        "starts_at",
        "expires_at",
        "is_active",
    )

    list_editable = (
        "is_active",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "starts_at",
        "expires_at",
        "created_at",
    )

    search_fields = (
        "code",
    )

    readonly_fields = (
        "used_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer_name",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "shipping_city",
        "placed_at",
    )

    list_editable = (
        "status",
        "payment_status",
    )

    list_filter = (
        "status",
        "payment_status",
        "shipping_country",
        "shipping_city",
        "placed_at",
        "updated_at",
    )

    search_fields = (
        "order_number",
        "customer_name",
        "customer_email",
        "customer_phone",
        "user__username",
        "user__email",
        "shipping_city",
        "shipping_district",
        "shipping_street",
    )

    autocomplete_fields = (
        "user",
        "coupon",
    )

    readonly_fields = (
        "order_number",
        "placed_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "coupon",
    )

    date_hierarchy = "placed_at"

    ordering = (
        "-placed_at",
    )

    inlines = (
        OrderItemInline,
        ShipmentInline,
    )

    fieldsets = (
        (
            "معلومات الطلب",
            {
                "fields": (
                    "order_number",
                    "user",
                    "coupon",
                    "status",
                    "payment_status",
                )
            },
        ),
        (
            "بيانات العميل",
            {
                "fields": (
                    "customer_name",
                    "customer_email",
                    "customer_phone",
                )
            },
        ),
        (
            "عنوان الشحن",
            {
                "fields": (
                    "shipping_country",
                    "shipping_city",
                    "shipping_district",
                    "shipping_street",
                    "shipping_building_number",
                    "shipping_postal_code",
                    "shipping_notes",
                )
            },
        ),
        (
            "القيم المالية",
            {
                "fields": (
                    "subtotal",
                    "discount_amount",
                    "shipping_amount",
                    "tax_amount",
                    "total_amount",
                )
            },
        ),
        (
            "الملاحظات",
            {
                "fields": (
                    "customer_notes",
                    "admin_notes",
                )
            },
        ),
        (
            "التواريخ",
            {
                "fields": (
                    "placed_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "variant_name",
        "sku",
        "unit_price",
        "quantity",
        "total_price",
    )

    list_filter = (
        "order__status",
        "order__payment_status",
    )

    search_fields = (
        "order__order_number",
        "product_name",
        "variant_name",
        "sku",
        "product__name",
    )

    autocomplete_fields = (
        "order",
        "product",
        "variant",
    )

    readonly_fields = (
        "total_price",
    )

    list_select_related = (
        "order",
        "product",
        "variant",
    )


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "shipping_company",
        "tracking_number",
        "status",
        "shipped_at",
        "delivered_at",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "shipping_company",
        "shipped_at",
        "delivered_at",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "shipping_company",
        "tracking_number",
    )

    autocomplete_fields = (
        "order",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "order",
    )

    ordering = (
        "-created_at",
    )