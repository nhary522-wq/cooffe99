from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .domain_models import (CropProfile, ProcessingMethod, ProductCompatibility,
    QualityInspection, RoastBatch, Supplier, ToolBundle, ToolBundleItem,
    ToolProfile, VariantCommercialData)
from .importers import parse_catalog_csv, save_catalog_rows
from .inventory import apply_inventory_movement
from .models import Brand, Category, Product, ProductVariant


class CatalogDomainTests(TestCase):
    def setUp(self):
        self.crops=Category.objects.create(name="محاصيل",slug="crops")
        self.tools=Category.objects.create(name="أدوات",slug="tools")
        self.roastery=Brand.objects.create(name="محمصة اختبار",slug="test-roastery",brand_type="roastery")
        self.supplier=Supplier.objects.create(name="مورد اختبار",slug="supplier",supplier_type="wholesaler")
        self.crop=Product.objects.create(category=self.crops,brand=self.roastery,product_type="crop",name="محصول",slug="crop-domain",sku="CROP-D",description="وصف",price=60,stock=5,country="إثيوبيا")
        self.tool=Product.objects.create(category=self.tools,product_type="tool",name="طاحونة",slug="tool-domain",sku="TOOL-D",description="وصف",price=200,stock=3)

    def test_extensible_roastery_supplier_and_crop(self):
        process=ProcessingMethod.objects.create(name="لاهوائية",slug="anaerobic")
        profile=CropProfile.objects.create(product=self.crop,processing_method=process,moisture_percentage=10,water_activity=Decimal("0.55"))
        self.assertEqual(profile.processing_method,process); self.assertTrue(self.supplier.is_active)

    def test_variant_prices_and_internal_data_not_public(self):
        variant=ProductVariant.objects.create(product=self.crop,name="250 جرام",sku="CROP-250",price=75,stock=10)
        commercial=VariantCommercialData.objects.create(variant=variant,supplier=self.supplier,weight_grams=250,purchase_cost=30,shipping_cost=5,supplier_url="https://supplier.invalid/item")
        self.assertEqual(commercial.price_per_100g,Decimal("30.00")); self.assertEqual(commercial.final_cost,Decimal("35")); self.assertEqual(commercial.estimated_cups,16)
        response=self.client.get(reverse("catalog:product_detail",args=[self.crop.slug])); self.assertNotContains(response,"supplier.invalid"); self.assertNotContains(response,"تكلفة الشراء")

    def test_freshness_and_quality_validation(self):
        batch=RoastBatch.objects.create(product=self.crop,roastery=self.roastery,batch_number="B1",roast_date=timezone.localdate()-timedelta(days=15),roast_level="medium",produced_quantity=5)
        self.assertEqual(batch.freshness_status,"في أفضل فترة استخدام")
        inspection=QualityInspection(supplier=self.supplier,product=self.tool,receipt_batch="R1",received_at=timezone.localdate(),received_quantity=2,accepted_quantity=2,rejected_quantity=1)
        with self.assertRaises(ValidationError): inspection.full_clean()

    def test_bundle_and_compatibility(self):
        accessory=Product.objects.create(category=self.tools,product_type="tool",name="فلاتر",slug="filters-domain",sku="FILTER-D",description="x",price=20,stock=8)
        ProductCompatibility.objects.create(source=self.tool,target=accessory,relation_type="compatible",reason="المقاس مناسب")
        bundle=ToolBundle.objects.create(name="باقة",slug="bundle",bundle_price=190); ToolBundleItem.objects.create(bundle=bundle,product=self.tool,quantity=1); ToolBundleItem.objects.create(bundle=bundle,product=accessory,quantity=2)
        self.assertEqual(bundle.original_price,Decimal("240")); self.assertEqual(bundle.savings,Decimal("50")); self.assertEqual(bundle.available_stock,3)

    def test_atomic_inventory_reservation(self):
        variant=ProductVariant.objects.create(product=self.tool,name="أساسي",sku="TOOL-V",price=200,stock=5)
        apply_inventory_movement(variant.pk,"reserve",2,reference="TEST")
        commercial=VariantCommercialData.objects.get(variant=variant); self.assertEqual(commercial.reserved_stock,2); self.assertEqual(commercial.available_stock,3)
        with self.assertRaises(ValidationError): apply_inventory_movement(variant.pk,"out",4)

    def test_unpublished_and_filters(self):
        self.crop.is_published=False; self.crop.save(); self.assertEqual(self.client.get(reverse("catalog:digital_card",args=[self.crop.slug])).status_code,404)
        response=self.client.get(reverse("catalog:tools"),{"material":"steel"}); self.assertEqual(response.status_code,200)

    def test_csv_preview_and_atomic_save(self):
        content=("sku,name,commercial_name,slug,category_slug,roastery_slug,country,region,farm,producer,variety,price,stock,is_published\n"
                 "CSV-1,محصول CSV,,csv-crop,crops,test-roastery,كينيا,,,,SL28,80,4,true\n").encode()
        rows,errors=parse_catalog_csv(SimpleUploadedFile("crops.csv",content),"crops")
        self.assertFalse(errors); created,updated=save_catalog_rows(rows,"crops"); self.assertEqual((created,updated),(1,0)); self.assertTrue(Product.objects.filter(sku="CSV-1",product_type="crop").exists())

    def test_import_requires_staff(self):
        user=get_user_model().objects.create_user("normal-import",password="pass12345"); self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("catalog:import_catalog",args=["crops"])).status_code,302)

    def test_unsafe_document_rejected(self):
        self.crop.origin_certificate=SimpleUploadedFile("danger.exe",b"not executable")
        with self.assertRaises(ValidationError): self.crop.full_clean()
