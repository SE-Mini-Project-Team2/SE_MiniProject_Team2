
from django.conf import settings
from django.db import models
from django.db.models import Q


class CartItem(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "book"],
                name="unique_customer_book_cart_item",
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1) & Q(quantity__lte=10),
                name="cart_quantity_between_1_and_10",
            ),
        ]

    @property
    def line_total(self):
        return self.book.price * self.quantity

    def __str__(self):
        return f"{self.customer.username} - {self.book.title}"
