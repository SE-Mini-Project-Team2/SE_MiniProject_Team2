from django.db import transaction

from cart.models import CartItem

from .models import Order, OrderItem


class EmptyCartError(Exception):
    """Raised when a customer tries to place an order with no cart items."""


def place_order(user):
    """
    FR-ORDER-01 / SEC-CTRL-09 / SEC-CTRL-11.

    Reads the customer's cart, copies each book's current price into the
    order (never trusting a client-submitted price), creates the Order and
    OrderItem rows, and clears the cart - all inside one transaction so a
    failure partway through leaves no partial order and an untouched cart.
    """
    with transaction.atomic():
        # select_for_update locks these rows for the duration of the
        # transaction so two simultaneous checkouts can't both read the
        # same cart and double-order it.
        items = list(
            CartItem.objects.select_for_update()
            .filter(customer=user)
            .select_related("book")
        )

        if not items:
            raise EmptyCartError("Your cart is empty.")

        order = Order.objects.create(customer=user)
        OrderItem.objects.bulk_create(
            OrderItem(
                order=order,
                book=item.book,
                quantity=item.quantity,
                unit_price=item.book.price,
            )
            for item in items
        )

        CartItem.objects.filter(customer=user).delete()

    return order
