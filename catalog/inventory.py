from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F

from .domain_models import InventoryMovement, VariantCommercialData
from .models import ProductVariant


@transaction.atomic
def apply_inventory_movement(variant_id, movement_type, quantity, **details):
    if quantity < 1: raise ValidationError("الكمية يجب أن تكون أكبر من صفر.")
    variant=ProductVariant.objects.select_for_update().get(pk=variant_id)
    commercial,_=VariantCommercialData.objects.select_for_update().get_or_create(variant=variant)
    if movement_type in {"out","damage"}:
        if commercial.available_stock < quantity: raise ValidationError("المخزون المتاح غير كافٍ.")
        ProductVariant.objects.filter(pk=variant.pk).update(stock=F("stock")-quantity)
    elif movement_type in {"in","return"}: ProductVariant.objects.filter(pk=variant.pk).update(stock=F("stock")+quantity)
    elif movement_type=="reserve":
        if commercial.available_stock < quantity: raise ValidationError("المخزون المتاح غير كافٍ للحجز.")
        VariantCommercialData.objects.filter(pk=commercial.pk).update(reserved_stock=F("reserved_stock")+quantity)
    elif movement_type=="release":
        if commercial.reserved_stock < quantity: raise ValidationError("الكمية المحجوزة أقل من المطلوب.")
        VariantCommercialData.objects.filter(pk=commercial.pk).update(reserved_stock=F("reserved_stock")-quantity)
    else: raise ValidationError("نوع حركة المخزون غير صالح.")
    return InventoryMovement.objects.create(variant=variant,movement_type=movement_type,quantity=quantity,**details)
