from django import forms

from .models import ProductReview


class CatalogCSVUploadForm(forms.Form):
    file = forms.FileField(label="ملف CSV")
    def clean_file(self):
        uploaded=self.cleaned_data["file"]
        if not uploaded.name.lower().endswith(".csv"): raise forms.ValidationError("يُسمح بملفات CSV فقط.")
        if uploaded.size > 2*1024*1024: raise forms.ValidationError("حجم الملف يجب ألا يتجاوز 2 ميجابايت.")
        return uploaded


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "quality_rating", "aroma_rating", "sweetness_rating",
                  "acidity_rating", "body_rating", "value_rating", "would_buy_again",
                  "title", "comment")
        widgets = {"comment": forms.Textarea(attrs={"rows": 5})}
