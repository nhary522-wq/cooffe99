from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .subscription_models import Subscription, SubscriptionBox


@transaction.atomic
def create_due_box(subscription_id):
    subscription = Subscription.objects.select_for_update().select_related("plan").get(pk=subscription_id)
    if subscription.status != "active" or subscription.next_shipment_at > timezone.now():
        return None
    period_start = timezone.localdate(subscription.next_shipment_at)
    period_end = period_start + timedelta(days=subscription.plan.interval_days - 1)
    box, _ = SubscriptionBox.objects.get_or_create(subscription=subscription, period_start=period_start, defaults={"period_end": period_end, "scheduled_at": subscription.next_shipment_at})
    subscription.next_shipment_at += timedelta(days=subscription.plan.interval_days)
    subscription.save(update_fields=["next_shipment_at", "updated_at"])
    return box
