from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import role_required

from .models import Order
from .services import EmptyCartError, place_order


@role_required("CUSTOMER")
@require_POST
def place_order_view(request):
    try:
        order = place_order(request.user)
    except EmptyCartError:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:view_cart")

    messages.success(request, f"Order #{order.pk} placed successfully.")
    return redirect("orders:history")


@role_required("CUSTOMER")
def order_history(request):
    # SEC-CTRL-08: scoped to the logged-in user; no client-supplied
    # customer id is ever read.
    orders = (
        Order.objects.filter(customer=request.user)
        .prefetch_related("items__book")
    )
    return render(request, "orders/order_history.html", {"orders": orders})
