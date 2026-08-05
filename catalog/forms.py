from django import forms

from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ("rating", "quality_rating", "aroma_rating", "sweetness_rating",
                  "acidity_rating", "body_rating", "value_rating", "would_buy_again",
                  "title", "comment")
        widgets = {"comment": forms.Textarea(attrs={"rows": 5})}

