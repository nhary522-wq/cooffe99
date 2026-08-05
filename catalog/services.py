from decimal import Decimal


STORE_ITEMS = (
    {"slug": "shalshali-ethiopian", "name": "شلشلي إثيوبي", "category": "crops", "origin": "إثيوبيا", "price": Decimal("68.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "محصول بإيحاءات فاكهية زاهية وقوام متوازن يناسب التقطير."},
    {"slug": "albahaa-blend", "name": "مزيج البهاء", "category": "crops", "origin": "مزيج مميز", "price": Decimal("72.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "مزيج غني بنكهات الشوكولاتة والمكسرات ولمسة حلوة."},
    {"slug": "balqees-yemen", "name": "بلقيس اليمن", "category": "crops", "origin": "اليمن", "price": Decimal("95.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "طابع يمني أصيل بإيحاءات التوابل والكاكاو."},
    {"slug": "ruby-colombia", "name": "روبي كلومبي", "category": "crops", "origin": "كولومبيا", "price": Decimal("70.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "حلاوة كراميل وحموضة ناعمة ونهاية نظيفة."},
    {"slug": "guji-ethiopian", "name": "قوجي إثيوبي", "category": "crops", "origin": "إثيوبيا", "price": Decimal("75.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "زهور وفواكه استوائية وحموضة مشرقة."},
    {"slug": "sidra-jazan", "name": "سدرة جازان", "category": "crops", "origin": "السعودية", "price": Decimal("88.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "محصول محلي بطابع غني وإيحاءات دافئة."},
    {"slug": "kenya-nyeri", "name": "كينيا نيري", "category": "crops", "origin": "كينيا", "price": Decimal("78.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "حموضة عصيرية وإيحاءات التوت الأحمر."},
    {"slug": "brazil-santos", "name": "برازيلي سانتوس", "category": "crops", "origin": "البرازيل", "price": Decimal("64.00"), "image": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=900&q=85", "description": "قوام كريمي ونكهات كاكاو وبندق."},
    {"slug": "espresso-cups", "name": "أكواب إسبريسو", "category": "tools", "origin": "التقديم", "price": Decimal("45.00"), "image": "/static/images/tools/espresso-cups.webp", "description": "أكواب أنيقة مناسبة لتقديم جرعات الإسبريسو."},
    {"slug": "manual-grinder", "name": "مطحنة يدوية", "category": "tools", "origin": "الطحن", "price": Decimal("129.00"), "image": "/static/images/tools/manual-grinder.webp", "description": "درجات طحن متعددة وتحكم عملي لمختلف طرق التحضير."},
    {"slug": "coffee-dripper", "name": "قمع تقطير", "category": "tools", "origin": "التقطير", "price": Decimal("55.00"), "image": "/static/images/tools/coffee-dripper.webp", "description": "قمع لاستخلاص متوازن وواضح للقهوة المقطرة."},
    {"slug": "coffee-scale", "name": "ميزان قهوة", "category": "tools", "origin": "الدقة", "price": Decimal("89.00"), "image": "/static/images/tools/coffee-scale.webp", "description": "قياس دقيق للقهوة والماء ووقت الاستخلاص."},
    {"slug": "coffee-filters", "name": "فلاتر جميع المقاسات", "category": "tools", "origin": "الفلاتر", "price": Decimal("35.00"), "image": "/static/images/tools/coffee-filters.webp", "description": "مقاسات متنوعة تناسب أدوات التقطير المختلفة."},
    {"slug": "coffee-grinders", "name": "مطاحن القهوة", "category": "tools", "origin": "الطحن", "price": Decimal("249.00"), "image": "/static/images/tools/coffee-grinders.webp", "description": "مطاحن بخيارات متعددة لطحن متسق كل مرة."},
    {"slug": "pour-over-tools", "name": "أدوات التقطير", "category": "tools", "origin": "التحضير", "price": Decimal("110.00"), "image": "/static/images/tools/pour-over-tools.webp", "description": "مجموعة عملية لطرق التقطير اليدوي."},
    {"slug": "brewing-kettles", "name": "أباريق التحضير", "category": "tools", "origin": "الصب", "price": Decimal("159.00"), "image": "/static/images/tools/brewing-kettles.webp", "description": "أباريق تمنحك تحكمًا أفضل في تدفق الماء."},
    {"slug": "coffee-accessories", "name": "ملحقات القهوة", "category": "tools", "origin": "الملحقات", "price": Decimal("49.00"), "image": "/static/images/tools/coffee-accessories.webp", "description": "ملحقات مختارة لتنظيم وتحسين تجربة التحضير."},
)


def get_store_item(slug):
    from .models import Product
    product = Product.objects.filter(slug=slug, is_active=True, is_published=True).select_related("category").first()
    if product:
        return {"slug": product.slug, "name": product.name,
                "category": "tools" if "tool" in product.category.slug else "crops",
                "origin": product.country or product.category.name, "price": product.price,
                "image": product.main_image.url if product.main_image else "/static/images/coffee-placeholder.svg",
                "description": product.short_description or product.description,
                "stock": product.stock if product.track_stock else 999999}
    return next((item for item in STORE_ITEMS if item["slug"] == slug), None)


def get_store_items(category=None, query=""):
    from .models import Product
    db_products = Product.objects.filter(is_active=True, is_published=True).select_related("category", "brand")
    if category == "crops": db_products = db_products.exclude(category__slug__icontains="tool")
    if category == "tools": db_products = db_products.filter(category__slug__icontains="tool")
    db_products = list(db_products)
    db_slugs = {p.slug for p in db_products}
    items = tuple({"slug": p.slug, "name": p.name, "category": "tools" if "tool" in p.category.slug else "crops", "origin": p.country or p.category.name,
                   "price": p.price, "image": p.main_image.url if p.main_image else "/static/images/coffee-placeholder.svg", "description": p.short_description or p.description}
                  for p in db_products) + tuple(item for item in STORE_ITEMS if item["slug"] not in db_slugs)
    if category in {"crops", "tools"}:
        items = tuple(item for item in items if item["category"] == category)
    normalized_query = query.strip().casefold()
    if normalized_query:
        items = tuple(
            item
            for item in items
            if normalized_query in item["name"].casefold()
            or normalized_query in item["description"].casefold()
            or normalized_query in item["origin"].casefold()
        )
    return items
