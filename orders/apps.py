from django.apps import AppConfig


class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "orders"

    def ready(self):
        from . import subscription_models  # noqa: F401
        from . import signals  # noqa: F401
    verbose_name = "الطلبات والشحن"
