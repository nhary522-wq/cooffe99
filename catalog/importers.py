import csv
import io
from decimal import Decimal, InvalidOperation

from django.db import transaction

from .domain_models import Supplier, ToolProfile
from .models import Brand, Category, Product


HEADERS = {
    "crops": ["sku", "name", "commercial_name", "slug", "category_slug", "roastery_slug", "country", "region", "farm", "producer", "variety", "price", "stock", "is_published"],
    "tools": ["sku", "name", "commercial_name", "slug", "category_slug", "brand_slug", "supplier_slug", "model_number", "country_of_manufacture", "price", "stock", "is_published"],
}


def parse_catalog_csv(uploaded_file, kind):
    if kind not in HEADERS: raise ValueError("نوع الاستيراد غير صالح.")
    text = uploaded_file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    missing = [name for name in HEADERS[kind] if name not in (reader.fieldnames or [])]
    if missing: return [], [{"row": 1, "message": "أعمدة ناقصة: " + ", ".join(missing)}]
    rows, errors, seen = [], [], set()
    for number, raw in enumerate(reader, 2):
        row = {key: (raw.get(key) or "").strip() for key in HEADERS[kind]}
        required = ["sku", "name", "slug", "category_slug", "price"]
        absent = [key for key in required if not row[key]]
        if absent: errors.append({"row": number, "message": "حقول إلزامية فارغة: " + ", ".join(absent)}); continue
        if row["sku"] in seen: errors.append({"row": number, "message": "SKU مكرر داخل الملف."}); continue
        seen.add(row["sku"])
        try:
            if Decimal(row["price"]) < 0: raise InvalidOperation
            row["stock"] = int(row["stock"] or 0)
            if row["stock"] < 0: raise ValueError
        except (InvalidOperation, ValueError): errors.append({"row": number, "message": "السعر أو المخزون غير صالح."}); continue
        if not Category.objects.filter(slug=row["category_slug"]).exists(): errors.append({"row": number, "message": "التصنيف غير موجود."}); continue
        relation_slug = row.get("roastery_slug") or row.get("brand_slug")
        if relation_slug and not Brand.objects.filter(slug=relation_slug).exists(): errors.append({"row": number, "message": "المحمصة أو العلامة غير موجودة."}); continue
        if kind == "tools" and row.get("supplier_slug") and not Supplier.objects.filter(slug=row["supplier_slug"]).exists(): errors.append({"row": number, "message": "المورد غير موجود."}); continue
        rows.append(row)
    return rows, errors


@transaction.atomic
def save_catalog_rows(rows, kind):
    created = updated = 0
    for row in rows:
        category = Category.objects.get(slug=row["category_slug"])
        brand_slug = row.get("roastery_slug") or row.get("brand_slug")
        brand = Brand.objects.filter(slug=brand_slug).first() if brand_slug else None
        defaults = {"name": row["name"], "commercial_name": row["commercial_name"], "slug": row["slug"], "category": category, "brand": brand,
                    "description": row["commercial_name"] or row["name"], "price": Decimal(row["price"]), "stock": int(row["stock"]),
                    "product_type": "crop" if kind == "crops" else "tool", "is_published": row["is_published"].lower() in {"1", "true", "yes", "نعم"}}
        if kind == "crops": defaults.update({key: row[key] for key in ("country", "region", "farm", "producer", "variety")})
        else: defaults.update({key: row[key] for key in ("model_number", "country_of_manufacture")})
        product, was_created = Product.objects.update_or_create(sku=row["sku"], defaults=defaults)
        if kind == "tools":
            supplier = Supplier.objects.filter(slug=row.get("supplier_slug")).first() if row.get("supplier_slug") else None
            ToolProfile.objects.update_or_create(product=product, defaults={"supplier": supplier})
        created += int(was_created); updated += int(not was_created)
    return created, updated
