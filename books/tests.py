
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
            email="seller_test@example.com",
            password="test-password",
            role="SELLER",
        )
        cls.customer = User.objects.create_user(
            username="customer_test",
            email="customer_test@example.com",
            password="test-password",
            role="CUSTOMER",
        )

        cls.book = Book.objects.create(
            title="Python Programming",
            author="Test Author",
            price="250.00",
            description="A book for learning Python.",
            seller=cls.seller,
        )

    def test_book_list_page_loads(self):
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)

    def test_book_list_displays_book(self):
        response = self.client.get(reverse("books:list"))
        self.assertContains(response, "Python Programming")

    def test_search_by_title(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "Python"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_by_author(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "Test Author"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_no_results(self):
        response = self.client.get(
            reverse("books:search"),
            {"q": "No matching book"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Python Programming")

    def test_seller_can_add_book(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "New Test Book",
                "author": "Another Author",
                "price": "150.00",
                "description": "A newly added book.",
            },
        )
        self.assertRedirects(response, reverse("books:list"))
        self.assertTrue(
            Book.objects.filter(title="New Test Book").exists()
        )

    def test_customer_cannot_add_book(self):
        self.client.force_login(self.customer)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Customer Book",
                "author": "Customer Author",
                "price": "100.00",
                "description": "Should not be added.",
            },
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(
            Book.objects.filter(title="Customer Book").exists()
        )

    def test_book_list_shows_add_to_cart_for_logged_in_user(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add to Cart")
