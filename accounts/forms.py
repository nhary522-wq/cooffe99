import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CoffeeJournalEntry, Profile


class CoffeeJournalForm(forms.ModelForm):
    class Meta:
        model = CoffeeJournalEntry
        exclude = ("user", "created_at", "updated_at")
        widgets = {"experienced_at": forms.DateTimeInput(attrs={"type": "datetime-local"}), "notes": forms.Textarea(attrs={"rows": 4}), "recipe": forms.Textarea(attrs={"rows": 5})}

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("product") and not (cleaned.get("external_product_name") or "").strip(): self.add_error("external_product_name", "اختر منتجًا أو أدخل اسم قهوة خارجية.")
        image = cleaned.get("image")
        if image and image.size > 5 * 1024 * 1024: self.add_error("image", "حجم الصورة يجب ألا يتجاوز 5 ميجابايت.")
        return cleaned


def normalize_phone(value):
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("00966"):
        digits = digits[2:]
    elif digits.startswith("05"):
        digits = "966" + digits[1:]
    return digits


class RegistrationForm(forms.Form):
    first_name = forms.CharField(label="الاسم الأول", max_length=150)
    last_name = forms.CharField(label="الاسم الثاني", max_length=150)
    email = forms.EmailField(label="البريد الإلكتروني", required=False)
    phone = forms.CharField(label="رقم الجوال", max_length=30, required=False)
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
    password_confirm = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        email = (cleaned_data.get("email") or "").strip().lower()
        phone = normalize_phone(cleaned_data.get("phone"))
        password = cleaned_data.get("password")

        if not email and not phone:
            raise ValidationError("أدخل البريد الإلكتروني أو رقم الجوال.")
        if phone and (len(phone) != 12 or not phone.startswith("9665")):
            self.add_error("phone", "أدخل رقم جوال سعوديًا صحيحًا.")

        user_model = get_user_model()
        if email and user_model.objects.filter(email__iexact=email).exists():
            self.add_error("email", "البريد الإلكتروني مستخدم بالفعل.")
        if phone and Profile.objects.filter(phone=phone).exists():
            self.add_error("phone", "رقم الجوال مستخدم بالفعل.")
        if password != cleaned_data.get("password_confirm"):
            self.add_error("password_confirm", "كلمتا المرور غير متطابقتين.")
        elif password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error("password", error)

        cleaned_data["email"] = email
        cleaned_data["phone"] = phone
        return cleaned_data


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="رقم الجوال أو البريد الإلكتروني",
        max_length=254,
    )
    password = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
