
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from books.models import Book


class Command(BaseCommand):
    help = "Create 10,000 synthetic books for search performance testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=10000,
            help="Number of performance-test books to create.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]

        if count < 1:
            self.stderr.write("Count must be greater than zero.")
            return

        # Reuse an existing seller when possible.
        seller = User.objects.filter(role="SELLER").first()

        if seller is None:
            self.stderr.write(
                self.style.ERROR(
                    "No seller account exists. Create a seller first."
                )
            )
            return

        # Reuse existing performance records if the command is rerun.
        # The dedicated marker makes cleanup straightforward.
        marker = "[PERF-TEST]"

        existing = Book.objects.filter(
            title__startswith=marker
        )

        existing.delete()

        books = []

        for i in range(count):
            books.append(
                Book(
                    title=f"{marker} Book {i + 1:05d}",
                    author=f"Author {(i % 500) + 1:03d}",
                    seller=seller,
                    price=10 + (i % 990) / 10,
                    description=(
                        f"Synthetic performance-test book number {i + 1}."
                    ),
                )
            )

        Book.objects.bulk_create(books, batch_size=500)

        created = Book.objects.filter(
            title__startswith=marker
        ).count()

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} performance-test books."
            )
        )
