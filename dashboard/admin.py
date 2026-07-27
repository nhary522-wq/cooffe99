from django.contrib import admin

from .models import AdminActivityLog


@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action",
        "app_label",
        "model_name",
        "object_repr",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "action",
        "app_label",
        "model_name",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "description",
        "ip_address",
        "user_agent",
    )

    readonly_fields = (
        "user",
        "action",
        "app_label",
        "model_name",
        "object_id",
        "object_repr",
        "description",
        "ip_address",
        "user_agent",
        "created_at",
    )

    list_select_related = (
        "user",
    )

    date_hierarchy = "created_at"

    ordering = (
        "-created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser