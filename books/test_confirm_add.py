from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from cart.models import CartItem

User = get_user_model()


class ConfirmAddToCartTests(TestCase):
    """The Add to Cart pop-up is shown to customers only."""

    def setUp(self):
        self.customer = User.objects.create_user(
            username="conf-c", email="conf-c@example.com",
            password="TestPass123!Secure", role="CUSTOMER",
        )
        self.seller = User.objects.create_user(
            username="conf-s", email="conf-s@example.com",
            password="TestPass456!Secure", role="SELLER",
        )
        self.book = Book.objects.create(
            title="Confirm Book", author="Test Author",
            price="100.00", seller=self.seller,
        )

    def test_customer_sees_popup_with_both_choices(self):
        self.client.force_login(self.customer)

        response = self.client.get(reverse("books:list"))

        self.assertContains(response, 'id="confirm-add"')
        self.assertContains(response, ">Discard</button>")
        self.assertContains(response, ">Add to Cart</button>")
        self.assertContains(response, "data-confirm-add")
        self.assertContains(response, 'data-book-title="Confirm Book"')

    def test_popup_is_on_search_results_too(self):
        self.client.force_login(self.customer)

        response = self.client.get(reverse("books:search"), {"q": "Confirm"})

        self.assertContains(response, 'id="confirm-add"')

    def test_seller_and_anonymous_do_not_get_popup(self):
        response = self.client.get(reverse("books:list"))
        self.assertNotContains(response, 'id="confirm-add"')

        self.client.force_login(self.seller)
        response = self.client.get(reverse("books:list"))
        self.assertNotContains(response, 'id="confirm-add"')

    def test_book_title_is_escaped_in_popup_data(self):
        Book.objects.create(
            title='"><script>alert(1)</script>', author="X",
            price="5.00", seller=self.seller,
        )
        self.client.force_login(self.customer)

        response = self.client.get(reverse("books:list"))

        self.assertNotContains(response, "<script>alert(1)")

    def test_add_to_cart_still_works_server_side(self):
        self.client.force_login(self.customer)

        self.client.post(reverse("cart:add_to_cart", args=[self.book.id]))

        self.assertEqual(CartItem.objects.count(), 1)
