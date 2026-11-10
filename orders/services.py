from django.db import transaction

from cart.models import CartItem

from .models import Order, OrderItem


class EmptyCartError(Exception):
    """Raised when a customer tries to place an order with no cart items."""


class BookSoldError(Exception):
    """Raised when a book in the cart was sold to someone else first."""

    def __init__(self, titles):
        super().__init__("Book already sold.")
        self.titles = titles


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
            CartItem.objects.select_for_update(of=("self", "book"))
            .filter(customer=user)
            .select_related("book")
        )

        if not items:
            raise EmptyCartError("Your cart is empty.")

        # The books are locked above with the cart rows. Refuse the whole
        # order if any has already been sold, so one copy is never sold twice.
        sold_ids = set(
            OrderItem.objects.filter(
                book_id__in=[item.book_id for item in items]
            ).values_list("book_id", flat=True)
        )
        sold = [item.book.title for item in items if item.book_id in sold_ids]
        if sold:
            raise BookSoldError(sold)

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
