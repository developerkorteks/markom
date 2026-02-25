from .cart import Cart


def cart_context(request):
    """
    Inject cart info ke semua template.
    Hanya untuk user yang sudah login dan berstatus sales.
    """
    if request.user.is_authenticated and hasattr(request.user, 'is_sales') and request.user.is_sales:
        cart = Cart(request)
        return {
            'navbar_cart_total': cart.get_total_quantity(),
            'navbar_cart_unique': cart.get_total_unique(),
        }
    return {
        'navbar_cart_total': 0,
        'navbar_cart_unique': 0,
    }
