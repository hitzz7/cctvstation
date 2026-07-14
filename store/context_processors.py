from .models import Category, Cart

def navbar_categories(request):
    categories = Category.objects.filter(is_active=True, parent=None)
    return {'navbar_categories': categories}

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = cart.get_total_quantity()
        except Cart.DoesNotExist:
            count = 0
    else:
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
                count = cart.get_total_quantity()
            except Cart.DoesNotExist:
                count = 0
        else:
            count = 0
    return {'cart_count': count}
