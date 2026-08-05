from django.db import migrations


def seed_methods(apps, schema_editor):
    BrewMethod = apps.get_model("core", "BrewMethod")
    methods = [
        ("V60", "v60", "ترشيح يدوي واضح ومتوازن", "medium", 4, 20, 300, "1:15", "متوسط", 93),
        ("كيمكس", "chemex", "قهوة نقية بقوام خفيف", "medium", 6, 30, 500, "1:16", "متوسط خشن", 93),
        ("فرنش برس", "french-press", "تحضير غني وسهل", "easy", 5, 30, 450, "1:15", "خشن", 94),
        ("إسبريسو", "espresso", "استخلاص مركز وكثيف", "advanced", 1, 18, 36, "1:2", "ناعم", 93),
        ("كولد برو", "cold-brew", "قهوة باردة ناعمة", "easy", 720, 80, 1000, "1:12", "خشن", 20),
        ("إيروبرس", "aeropress", "طريقة مرنة وسريعة", "medium", 3, 17, 250, "1:15", "متوسط ناعم", 88),
        ("كاليتا", "kalita", "تقطير متوازن بثلاث فتحات", "medium", 4, 20, 300, "1:15", "متوسط", 92),
        ("القهوة المقطرة", "drip-coffee", "تحضير يومي عملي", "easy", 6, 30, 500, "1:16", "متوسط", 92),
        ("القهوة السعودية", "saudi-coffee", "قهوة سعودية تقليدية بالهيل", "medium", 20, 40, 1000, "1:25", "خشن", 96),
    ]
    for name, slug, short, difficulty, duration, coffee, water, ratio, grind, temp in methods:
        BrewMethod.objects.get_or_create(slug=slug, defaults={"name": name, "short_description": short, "description": short, "difficulty": difficulty, "duration_minutes": duration, "coffee_grams": coffee, "water_ml": water, "ratio": ratio, "grind_size": grind, "water_temperature": temp, "is_published": True})


class Migration(migrations.Migration):
    dependencies = [("core", "0002_brewtool_contentcategory_brewmethod_coffeecontent_and_more")]
    operations = [migrations.RunPython(seed_methods, migrations.RunPython.noop)]
