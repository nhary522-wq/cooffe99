from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.services import sync_order_loyalty
from .models import Order


@receiver(post_save, sender=Order)
def update_loyalty_for_order(sender, instance, **kwargs):
    sync_order_loyalty(instance)
