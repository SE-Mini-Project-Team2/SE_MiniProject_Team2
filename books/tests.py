from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Book


User = get_user_model()


class BookFeatureTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seller = User.objects.create_user(
            username="seller_test",
            password="test-password",
            role="SELLER",
        )
        cls.customer = User.objects.create_user(
            username="customer_test",
            password="test-password",
            role="CUSTOMER",
        )

        cls.book = Book.objects.create(
            title="Python Programming",
            author="Alex Writer",
            price=Decimal("499.99"),
            description="A programming book.",
            seller=cls.seller,
        )

    def test_public_book_browsing(self):
        response = self.client.get(reverse("books:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_matches_title_case_insensitively(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "PYTHON"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_matches_author(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "alex"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_with_no_matches_shows_no_results(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "NoSuchBook"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 0)

    def test_search_rejects_more_than_100_characters(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "a" * 101},
        )

        self.assertEqual(response.status_code, 400)

    def test_seller_can_add_book(self):
        self.client.force_login(self.seller)

        response = self.client.post(
            reverse("books:add"),
            {
                "title": "New Book",
                "author": "New Author",
                "price": "199.50",
                "description": "A test listing.",
            },
        )

        self.assertRedirects(response, reverse("books:list"))

        book = Book.objects.get(title="New Book")
        self.assertEqual(book.seller, self.seller)
        self.assertEqual(book.price, Decimal("199.50"))

    def test_customer_cannot_add_book(self):
        self.client.force_login(self.customer)

        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Unauthorized Book",
                "author": "Someone",
                "price": "100.00",
                "description": "",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            Book.objects.filter(title="Unauthorized Book").exists()
        )

    def test_anonymous_visitor_cannot_add_book(self):
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Anonymous Book",
                "author": "Someone",
                "price": "100.00",
                "description": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Book.objects.filter(title="Anonymous Book").exists()
        )