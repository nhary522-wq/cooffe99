import re

from django import forms
from .subscription_models import Subscription


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ("address", "start_date", "coffee_preferences", "grind_type", "excluded_products")
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "excluded_products": forms.CheckboxSelectMultiple()}
from django.core.exceptions import ValidationError


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ("cash_on_delivery", "الدفع عند الاستلام"),
        ("mada", "مدى"),
        ("card", "بطاقة بنكية"),
        ("apple_pay", "Apple Pay"),
    )

    first_name = forms.CharField(label="الاسم الأول", max_length=75)
    last_name = forms.CharField(label="الاسم الثاني", max_length=75)
    email = forms.EmailField(label="البريد الإلكتروني")
    phone = forms.CharField(label="رقم الجوال", max_length=30)
    city = forms.CharField(label="المدينة", max_length=100)
    district = forms.CharField(label="الحي", max_length=100)
    street = forms.CharField(label="الشارع", max_length=200)
    building_number = forms.CharField(
        label="رقم المبنى",
        max_length=50,
        required=False,
    )
    postal_code = forms.CharField(
        label="الرمز البريدي",
        max_length=20,
        required=False,
    )
    payment_method = forms.ChoiceField(
        label="طريقة الدفع",
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
    )
    notes = forms.CharField(
        label="ملاحظات التوصيل",
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )

    def clean_phone(self):
        phone = re.sub(r"\D", "", self.cleaned_data["phone"])
        if phone.startswith("00966"):
            phone = phone[2:]
        elif phone.startswith("05"):
            phone = "966" + phone[1:]
        if len(phone) != 12 or not phone.startswith("9665"):
            raise ValidationError("أدخل رقم جوال سعوديًا صحيحًا.")
        return phone
