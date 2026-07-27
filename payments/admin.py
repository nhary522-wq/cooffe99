from django.contrib import admin

from .models import Payment, PaymentMethod, Refund


class RefundInline(admin.TabularInline):
    model = Refund

    extra = 0

    show_change_link = True

    fields = (
        "refund_number",
        "amount",
        "status",
        "gateway_reference",
        "completed_at",
        "created_at",
    )

    readonly_fields = (
        "refund_number",
        "created_at",
    )


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "method_type",
        "display_order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "display_order",
        "is_active",
    )

    list_filter = (
        "method_type",
        "is_active",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "name",
        "method_type",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "display_order",
        "name",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "order",
        "payment_method",
        "status",
        "amount",
        "currency",
        "gateway_name",
        "paid_at",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "payment_method",
        "currency",
        "gateway_name",
        "paid_at",
        "created_at",
    )

    search_fields = (
        "transaction_id",
        "order__order_number",
        "gateway_reference",
        "gateway_name",
        "failure_reason",
    )

    autocomplete_fields = (
        "order",
        "payment_method",
    )

    readonly_fields = (
        "transaction_id",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "order",
        "payment_method",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    inlines = (
        RefundInline,
    )

    fieldsets = (
        (
            "معلومات العملية",
            {
                "fields": (
                    "transaction_id",
                    "order",
                    "payment_method",
                    "status",
                    "amount",
                    "currency",
                )
            },
        ),
        (
            "بوابة الدفع",
            {
                "fields": (
                    "gateway_name",
                    "gateway_reference",
                    "failure_reason",
                )
            },
        ),
        (
            "التواريخ",
            {
                "fields": (
                    "paid_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "refund_number",
        "payment",
        "amount",
        "status",
        "completed_at",
        "created_at",
    )

    list_editable = (
        "status",
    )

    list_filter = (
        "status",
        "completed_at",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "refund_number",
        "payment__transaction_id",
        "payment__order__order_number",
        "gateway_reference",
        "reason",
        "admin_notes",
    )

    autocomplete_fields = (
        "payment",
    )

    readonly_fields = (
        "refund_number",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "payment",
        "payment__order",
    )

    ordering = (
        "-created_at",
    )