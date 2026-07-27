from django.conf import settings
from django.db import models


class AdminActivityLog(models.Model):
    ACTION_CHOICES = [
        ("create", "إضافة"),
        ("update", "تعديل"),
        ("delete", "حذف"),
        ("login", "تسجيل دخول"),
        ("logout", "تسجيل خروج"),
        ("other", "إجراء آخر"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="المستخدم",
        on_delete=models.SET_NULL,
        related_name="admin_activity_logs",
        blank=True,
        null=True,
    )

    action = models.CharField(
        "نوع الإجراء",
        max_length=20,
        choices=ACTION_CHOICES,
    )

    app_label = models.CharField(
        "اسم التطبيق",
        max_length=100,
        blank=True,
    )

    model_name = models.CharField(
        "اسم النموذج",
        max_length=100,
        blank=True,
    )

    object_id = models.CharField(
        "معرف العنصر",
        max_length=100,
        blank=True,
    )

    object_repr = models.CharField(
        "وصف العنصر",
        max_length=250,
        blank=True,
    )

    description = models.TextField(
        "تفاصيل الإجراء",
        blank=True,
    )

    ip_address = models.GenericIPAddressField(
        "عنوان IP",
        blank=True,
        null=True,
    )

    user_agent = models.TextField(
        "معلومات المتصفح",
        blank=True,
    )

    created_at = models.DateTimeField(
        "تاريخ الإجراء",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "سجل نشاط إداري"
        verbose_name_plural = "سجلات النشاط الإداري"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["app_label", "model_name"]),
        ]

    def __str__(self):
        username = self.user.get_username() if self.user else "مستخدم محذوف"
        return f"{username} - {self.get_action_display()}"