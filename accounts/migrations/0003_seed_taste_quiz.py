from django.db import migrations


def seed_quiz(apps, schema_editor):
    Question = apps.get_model("accounts", "TasteQuestion"); Answer = apps.get_model("accounts", "TasteAnswer")
    data = [
        ("flavor", "أي نكهات تفضل؟", [("فاكهية", "fruity", "fruity"), ("شوكولاتية", "chocolate", "chocolate"), ("مكسرات", "nuts", "nuts"), ("متوازنة", "balanced", "balanced")]),
        ("acidity", "ما مستوى الحموضة المفضل؟", [("منخفضة", "low", "1,2"), ("متوسطة", "medium", "3"), ("مرتفعة", "high", "4,5")]),
        ("body", "ما القوام المفضل؟", [("خفيف", "light", "light"), ("متوسط", "medium", "medium"), ("ثقيل", "heavy", "dark")]),
        ("roast", "ما درجة التحميص؟", [("فاتح", "light", "light"), ("متوسط", "medium", "medium"), ("غامق", "dark", "dark")]),
        ("brew", "ما طريقة التحضير؟", [("تقطير", "pour-over", "v60,drip"), ("إسبريسو", "espresso", "espresso"), ("فرنش برس", "press", "press")]),
        ("milk", "هل تشرب القهوة مع الحليب؟", [("مع الحليب", "with", "chocolate,dark"), ("بدون حليب", "without", "fruity,light")]),
        ("budget", "ما الميزانية التقريبية؟", [("اقتصادية", "economy", ""), ("متوسطة", "medium", ""), ("مفتوحة", "open", "")]),
        ("adventure", "هل تفضل الجديد أم المألوف؟", [("نكهات جديدة", "new", "fruity"), ("خيارات مألوفة", "familiar", "chocolate,nuts")]),
    ]
    for order, (key, text, answers) in enumerate(data):
        question, _ = Question.objects.get_or_create(key=key, defaults={"text": text, "display_order": order, "is_active": True})
        for answer_order, (label, value, tags) in enumerate(answers): Answer.objects.get_or_create(question=question, value=value, defaults={"text": label, "score_tags": tags, "display_order": answer_order})


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_coffeejournalentry_loyaltyaccount_loyaltysetting_and_more")]
    operations = [migrations.RunPython(seed_quiz, migrations.RunPython.noop)]
