def cart_summary(request):
    cart = request.session.get("cart", {})
    count = 0
    for quantity in cart.values():
        try:
            count += max(0, min(int(quantity), 20))
        except (TypeError, ValueError):
            continue
    return {"cart_item_count": count}
