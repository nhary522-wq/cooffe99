from django.db import IntegrityError, transaction
from django.db.models import F

from .models import LoyaltyAccount, LoyaltySetting, LoyaltyTransaction


@transaction.atomic
def sync_order_loyalty(order):
    if not order.user_id:
        return
    setting = LoyaltySetting.objects.first()
    if setting and not setting.is_enabled:
        return
    setting = setting or LoyaltySetting(points_per_riyal=1)
    account, _ = LoyaltyAccount.objects.select_for_update().get_or_create(user_id=order.user_id)
    earned = LoyaltyTransaction.objects.filter(order=order, transaction_type="earn").first()
    if order.status == "delivered" and not earned:
        points = int(order.total_amount * setting.points_per_riyal)
        if points <= 0: return
        try: LoyaltyTransaction.objects.create(account=account, order=order, transaction_type="earn", points=points, description=f"نقاط الطلب {order.order_number}")
        except IntegrityError: return
        LoyaltyAccount.objects.filter(pk=account.pk).update(balance=F("balance") + points, lifetime_earned=F("lifetime_earned") + points)
    elif order.status in {"cancelled", "refunded"} and earned and not LoyaltyTransaction.objects.filter(order=order, transaction_type="reverse").exists():
        points = -earned.points
        try: LoyaltyTransaction.objects.create(account=account, order=order, transaction_type="reverse", points=points, description=f"عكس نقاط الطلب {order.order_number}")
        except IntegrityError: return
        LoyaltyAccount.objects.filter(pk=account.pk).update(balance=F("balance") + points)
