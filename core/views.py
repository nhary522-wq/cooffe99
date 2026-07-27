from django.shortcuts import render


def home(request):
    """عرض الصفحة الرئيسية للمتجر."""
    return render(request, "home.html")