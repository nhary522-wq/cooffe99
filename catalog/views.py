from django.http import Http404
from django.shortcuts import render

from .services import get_store_item, get_store_items


def product_list(request, category=None):
    if category not in {None, "crops", "tools"}:
        raise Http404
    query = request.GET.get("q", "")[:100]
    category_titles = {
        None: "منتجات القهوة",
        "crops": "محاصيل القهوة",
        "tools": "أدوات القهوة",
    }
    return render(
        request,
        "catalog/product_list.html",
        {
            "items": get_store_items(category, query),
            "category": category,
            "category_title": category_titles[category],
            "query": query,
        },
    )


def product_detail(request, slug):
    item = get_store_item(slug)
    if not item:
        raise Http404
    related_items = tuple(
        related
        for related in get_store_items(item["category"])
        if related["slug"] != slug
    )[:3]
    return render(
        request,
        "catalog/product_detail.html",
        {"item": item, "related_items": related_items},
    )
