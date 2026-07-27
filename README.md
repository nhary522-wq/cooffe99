# cooffe99

متجر قهوة إلكتروني مبني باستخدام Django، ويتضمن لوحة إدارة مستقلة داخل:

```text
independent-admin-dashboard/
```

## تشغيل مشروع Django

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

يجب إعداد متغيرات البيئة المطلوبة محليًا داخل ملف `.env`، ولا يُرفع هذا الملف إلى المستودع.

## تشغيل لوحة الإدارة المستقلة

```powershell
cd independent-admin-dashboard
python -m http.server 4173
```

ثم افتح `http://localhost:4173`.
