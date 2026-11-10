from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Min


class BookQuerySet(models.QuerySet):
    def available(self):
        """Books that no placed order contains yet."""
        return self.filter(order_items__isnull=True)

    def with_sold_date(self):
        """Annotate sold_at: date of the first order containing the book."""
        return self.annotate(sold_at=Min("order_items__order__created_at"))


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    description = models.TextField(blank=True)
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="book_listings",
    )

    objects = BookQuerySet.as_manager()

    class Meta:
        ordering = ["title", "id"]

    @property
    def is_sold(self):
        return self.order_items.exists()

    def __str__(self):
        return f"{self.title} by {self.author}"