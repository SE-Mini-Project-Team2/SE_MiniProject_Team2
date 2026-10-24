import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User, UserRole
from books.models import Book

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Ishaan", "Reyansh", "Arjun", "Kabir", "Dev",
    "Rohan", "Sai", "Ananya", "Diya", "Saanvi", "Myra", "Aadhya", "Kiara",
    "Riya", "Anika", "Priya", "Neha", "James", "Olivia", "Liam", "Emma",
    "Noah", "Ava", "Mia", "Lucas", "Sofia", "Ethan",
]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Mehta", "Khan", "Reddy", "Iyer", "Nair",
    "Chopra", "Kapoor", "Joshi", "Rao", "Patel", "Singh", "Bose", "Mishra",
    "Smith", "Johnson", "Brown", "Garcia", "Miller", "Davis", "Wilson",
    "Martinez", "Clark", "Lewis",
]
ADJECTIVES = [
    "Silent", "Hidden", "Last", "Broken", "Golden", "Lost", "Secret",
    "Burning", "Distant", "Forgotten", "Quiet", "Crimson", "Endless",
    "Shattered", "Midnight", "Wandering", "Scarlet", "Frozen", "Sacred",
    "Restless",
]
NOUNS = [
    "Garden", "River", "Shadow", "Kingdom", "Ocean", "Mountain", "City",
    "Forest", "Empire", "Journey", "Letter", "Promise", "Harbor", "Orchard",
    "Library", "Bridge", "Island", "Winter", "Storm", "Flame",
]
TITLE_TEMPLATES = [
    "The {adj} {noun}",
    "{noun} of {adj2} {noun2}",
    "A {adj} {noun}",
    "The {noun} and the {noun2}",
    "{adj} {noun}",
]

DEFAULT_PASSWORD = "SeedPass!9"


class Command(BaseCommand):
    help = "Seed demo sellers and book listings for local testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sellers", type=int, default=100,
            help="Number of seller accounts to create (default 100).",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Delete existing seed-generated sellers (and their books) first.",
        )

    def handle(self, *args, **options):
        n_sellers = options["sellers"]
        rng = random.Random(42)  # fixed seed: reruns are reproducible

        if options["clear"]:
            existing = User.objects.filter(email__startswith="seller", email__endswith="@seed.test")
            count = existing.count()
            existing.delete()  # Book.seller is on_delete=PROTECT, so this
            # only succeeds if no orders reference those books; that's fine
            # for a fresh local db.
            self.stdout.write(f"Cleared {count} existing seed sellers.")

        created_sellers = 0
        created_books = 0

        with transaction.atomic():
            for i in range(1, n_sellers + 1):
                email = f"seller{i:03d}@seed.test"
                if User.objects.filter(email=email).exists():
                    continue

                name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
                seller = User.objects.create_user(
                    email=email,
                    password=DEFAULT_PASSWORD,
                    role=UserRole.SELLER,
                    name=name,
                )
                created_sellers += 1

                for _ in range(rng.randint(2, 3)):
                    template = rng.choice(TITLE_TEMPLATES)
                    title = template.format(
                        adj=rng.choice(ADJECTIVES), adj2=rng.choice(ADJECTIVES),
                        noun=rng.choice(NOUNS), noun2=rng.choice(NOUNS),
                    )
                    author = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
                    price = Decimal(rng.randrange(9900, 199900, 50)) / 100

                    Book.objects.create(
                        title=title,
                        author=author,
                        price=price,
                        description=f"A demo listing by {name} for local testing.",
                        seller=seller,
                    )
                    created_books += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created {created_sellers} sellers and {created_books} book listings. "
            f"Login as any seller with password '{DEFAULT_PASSWORD}'."
        ))
