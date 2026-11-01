from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
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
            price=Decimal("250.00"),
            description="A book for learning Python.",
            seller=cls.seller,
        )

    # FR-BOOK-01: Browse books

    def test_book_list_page_loads(self):
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)

    def test_book_list_displays_book_details(self):
        response = self.client.get(reverse("books:list"))
        self.assertContains(response, "Python Programming")
        self.assertContains(response, "Test Author")
        self.assertContains(response, "250.00")

    def test_book_list_shows_empty_catalogue_message(self):
        Book.objects.all().delete()
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No books are currently available.")

    def test_book_list_is_paginated_to_twenty_books(self):
        Book.objects.bulk_create([
            Book(
                title=f"Book {number:02d}",
                author="Pagination Author",
                price=Decimal("10.00"),
                seller=self.seller,
            )
            for number in range(1, 22)
        ])
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"].object_list), 20)
        self.assertTrue(response.context["books"].has_next())

    def test_book_list_second_page_displays_remaining_book(self):
        Book.objects.bulk_create([
            Book(
                title=f"Book {number:02d}",
                author="Pagination Author",
                price=Decimal("10.00"),
                seller=self.seller,
            )
            for number in range(1, 22)
        ])
        response = self.client.get(reverse("books:list"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"].object_list), 2)
        self.assertFalse(response.context["books"].has_next())

    # FR-BOOK-02: Search books

    def test_search_by_title(self):
        response = self.client.get(reverse("books:search"), {"q": "Python"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_by_author(self):
        response = self.client.get(
            reverse("books:search"), {"q": "Test Author"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_is_case_insensitive(self):
        response = self.client.get(
            reverse("books:search"), {"q": "pYtHoN"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_supports_partial_matches(self):
        response = self.client.get(
            reverse("books:search"), {"q": "Program"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Programming")

    def test_search_no_results(self):
        response = self.client.get(
            reverse("books:search"), {"q": "No matching book"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Python Programming")
        self.assertContains(response, "No books found matching your search.")

    def test_search_accepts_query_of_exactly_one_hundred_characters(self):
        response = self.client.get(
            reverse("books:search"), {"q": "x" * 100}
        )
        self.assertEqual(response.status_code, 200)

    def test_search_rejects_query_longer_than_one_hundred_characters(self):
        response = self.client.get(
            reverse("books:search"), {"q": "x" * 101}
        )
        self.assertEqual(response.status_code, 400)

    def test_search_results_are_paginated_to_twenty_books(self):
        Book.objects.bulk_create([
            Book(
                title=f"Python Book {number:02d}",
                author="Search Author",
                price=Decimal("10.00"),
                seller=self.seller,
            )
            for number in range(1, 22)
        ])
        response = self.client.get(
            reverse("books:search"), {"q": "Python"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"].object_list), 20)
        self.assertTrue(response.context["books"].has_next())

    # FR-BOOK-03: Seller book creation and access control

    def test_seller_can_open_add_book_page(self):
        self.client.force_login(self.seller)
        response = self.client.get(reverse("books:add"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_is_redirected_from_add_book_page(self):
        response = self.client.get(reverse("books:add"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_anonymous_user_cannot_create_book(self):
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Anonymous Book",
                "author": "Anonymous Author",
                "price": "100.00",
                "description": "Should not be created.",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Book.objects.filter(title="Anonymous Book").exists())

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
        new_book = Book.objects.get(title="New Test Book")
        self.assertEqual(new_book.seller, self.seller)
        self.assertEqual(new_book.price, Decimal("150.00"))

    def test_customer_receives_forbidden_when_opening_add_book_page(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("books:add"))
        self.assertEqual(response.status_code, 403)

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
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Book.objects.filter(title="Customer Book").exists())

    def test_submitted_seller_id_cannot_override_logged_in_seller(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Seller Ownership Test",
                "author": "Ownership Author",
                "price": "80.00",
                "description": "Ownership must come from request.user.",
                "seller": self.customer.pk,
            },
        )
        self.assertRedirects(response, reverse("books:list"))
        created_book = Book.objects.get(title="Seller Ownership Test")
        self.assertEqual(created_book.seller, self.seller)

    def test_add_book_rejects_missing_required_fields(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {"title": "", "author": "", "price": "100.00"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.filter(price=Decimal("100.00")).exists())

    def test_add_book_rejects_whitespace_only_title_and_author(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "   ",
                "author": "   ",
                "price": "100.00",
                "description": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.filter(price=Decimal("100.00")).exists())

    def test_add_book_rejects_zero_price(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Zero Price Book",
                "author": "Price Author",
                "price": "0.00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.filter(title="Zero Price Book").exists())

    def test_add_book_rejects_negative_price(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Negative Price Book",
                "author": "Price Author",
                "price": "-1.00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Book.objects.filter(title="Negative Price Book").exists()
        )

    def test_add_book_rejects_price_with_more_than_two_decimal_places(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Decimal Price Book",
                "author": "Price Author",
                "price": "10.999",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Book.objects.filter(title="Decimal Price Book").exists()
        )

    def test_add_book_accepts_valid_minimum_price(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Minimum Price Book",
                "author": "Price Author",
                "price": "0.01",
            },
        )
        self.assertRedirects(response, reverse("books:list"))
        self.assertTrue(
            Book.objects.filter(
                title="Minimum Price Book", price=Decimal("0.01")
            ).exists()
        )

    def test_add_book_rejects_title_longer_than_model_limit(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "T" * 256,
                "author": "Long Title Author",
                "price": "10.00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Book.objects.filter(author="Long Title Author").exists())

    def test_add_book_rejects_author_longer_than_model_limit(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "Long Author Book",
                "author": "A" * 256,
                "price": "10.00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Book.objects.filter(title="Long Author Book").exists()
        )

    def test_add_book_strips_surrounding_whitespace(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "  Clean Title  ",
                "author": "  Clean Author  ",
                "price": "12.50",
            },
        )
        self.assertRedirects(response, reverse("books:list"))
        self.assertTrue(
            Book.objects.filter(
                title="Clean Title", author="Clean Author"
            ).exists()
        )

    # Security-related checks

    def test_add_book_post_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.seller)
        response = csrf_client.post(
            reverse("books:add"),
            {
                "title": "CSRF Book",
                "author": "CSRF Author",
                "price": "10.00",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Book.objects.filter(title="CSRF Book").exists())

    def test_add_book_post_succeeds_with_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.seller)
        page = csrf_client.get(reverse("books:add"))
        self.assertEqual(page.status_code, 200)
        csrf_token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(
            reverse("books:add"),
            {
                "title": "CSRF Valid Book",
                "author": "CSRF Author",
                "price": "10.00",
            },
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertRedirects(response, reverse("books:list"))
        self.assertTrue(
            Book.objects.filter(title="CSRF Valid Book").exists()
        )

    def test_book_content_is_html_escaped_in_listing(self):
        Book.objects.create(
            title="<script>alert(1)</script>",
            author="HTML Author",
            price=Decimal("15.00"),
            seller=self.seller,
        )
        response = self.client.get(reverse("books:list"))
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_book_list_shows_add_to_cart_for_logged_in_user(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add to Cart")

    def test_anonymous_user_is_not_shown_add_to_cart_button(self):
        response = self.client.get(reverse("books:list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Add to Cart")
