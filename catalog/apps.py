from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self):
        from . import domain_models  # noqa: F401
    verbose_name = "المنتجات والكتالوج"
