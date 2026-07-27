from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


# -----------------------------------------------------------------------------
# تخصيص لوحة الإدارة
# -----------------------------------------------------------------------------

admin.site.site_header = "إدارة متجر كوفي 99"
admin.site.site_title = "لوحة إدارة المتجر"
admin.site.index_title = "مرحبًا بك في لوحة التحكم"


# -----------------------------------------------------------------------------
# روابط المشروع
# -----------------------------------------------------------------------------

urlpatterns = [
    # لوحة الإدارة
    path("admin/", admin.site.urls),

    # تطبيق الصفحة الرئيسية والإعدادات العامة
    path("", include("core.urls")),

    # تطبيق الحسابات
    path("accounts/", include("accounts.urls")),
    path("accounts/social/", include("allauth.urls")),

    # تطبيق المنتجات والتصنيفات
    path("catalog/", include("catalog.urls")),

    # تطبيق الطلبات
    path("orders/", include("orders.urls")),

    # تطبيق المدفوعات
    path("payments/", include("payments.urls")),

    # تطبيق لوحة التحكم
    path("dashboard/", include("dashboard.urls")),
]


# -----------------------------------------------------------------------------
# عرض ملفات media و static أثناء التطوير
# -----------------------------------------------------------------------------

if settings.DEBUG:
    # عرض الصور والملفات المرفوعة من مجلد media
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    # عرض الملفات الثابتة من STATIC_ROOT أثناء التطوير
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )
