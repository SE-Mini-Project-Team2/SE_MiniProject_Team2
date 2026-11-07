"""STP 16.4 integration scenarios IT-01 to IT-06, run across the real views.

IT-03 and IT-04 already exist in orders/tests.py; the scenarios here cover
the ones that had no dedicated end-to-end test.
"""

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserRole
from books.models import Book
from cart.models import CartItem
from orders.models import Order

User = get_user_model()
PASSWORD = "A-secure-unique-password-42"


def make_user(email, role):
    return User.objects.create_user(
        email=email, password=PASSWORD, name=email.split("@")[0], role=role
    )


class IT01SellerListingFoundByCustomer(TestCase):
    """IT-01: Seller creates a listing -> Customer searches for the book."""

    def test_it_01_listing_created_by_seller_is_searchable_by_customer(self):
        seller = make_user("it01-seller@example.com", UserRole.SELLER)
        customer = make_user("it01-customer@example.com", UserRole.CUSTOMER)

        self.client.force_login(seller)
        created = self.client.post(
            reverse("books:add"),
            {
                "title": "Integration Testing in Practice",
                "author": "Ada Verifier",
                "price": "349.50",
                "description": "Covers end-to-end scenarios.",
            },
        )
        self.assertRedirects(created, reverse("books:list"))
        self.client.logout()

        self.client.force_login(customer)
        found = self.client.get(reverse("books:search"), {"q": "integration testing"})

        self.assertEqual(found.status_code, 200)
        for stored_value in (
            "Integration Testing in Practice",
            "Ada Verifier",
            "349.50",
            "Covers end-to-end scenarios.",
        ):
            self.assertContains(found, stored_value)
        book = Book.objects.get(title="Integration Testing in Practice")
        self.assertEqual(book.seller, seller)


class IT05CrossCustomerAccessDenied(TestCase):
    """IT-05: Customer A requests Customer B's cart item / order."""

    def setUp(self):
        self.seller = make_user("it05-seller@example.com", UserRole.SELLER)
        self.book = Book.objects.create(
            title="Private Purchase", author="B. Owner", price="120.00", seller=self.seller
        )
        self.customer_a = make_user("it05-a@example.com", UserRole.CUSTOMER)
        self.customer_b = make_user("it05-b@example.com", UserRole.CUSTOMER)

    def test_it_05_customer_cannot_remove_or_see_another_customers_data(self):
        b_item = CartItem.objects.create(
            customer=self.customer_b, book=self.book, quantity=2
        )
        self.client.force_login(self.customer_b)
        self.client.post(reverse("orders:place"))
        b_order = Order.objects.get(customer=self.customer_b)
        self.client.logout()
        b_item_again = CartItem.objects.create(
            customer=self.customer_b, book=self.book, quantity=3
        )

        self.client.force_login(self.customer_a)

        # A tries to remove B's cart line: 404, B's line untouched.
        removal = self.client.post(
            reverse("cart:remove_from_cart", args=[b_item_again.pk])
        )
        self.assertEqual(removal.status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=b_item_again.pk).exists())

        # A's cart view and order history disclose nothing of B's.
        cart = self.client.get(reverse("cart:view_cart"))
        history = self.client.get(reverse("orders:history"))
        for response in (cart, history):
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "Private Purchase")
            self.assertNotContains(response, f"Order #{b_order.pk}")


class IT06SessionExpiryDuringProtectedOperation(TestCase):
    """IT-06: Session expires during a protected operation."""

    def test_it_06_expired_session_forces_login_and_changes_no_state(self):
        seller = make_user("it06-seller@example.com", UserRole.SELLER)
        customer = make_user("it06-customer@example.com", UserRole.CUSTOMER)
        book = Book.objects.create(
            title="Expiring Session", author="C. Clock", price="99.00", seller=seller
        )
        CartItem.objects.create(customer=customer, book=book, quantity=1)
        self.client.force_login(customer)
        self.assertEqual(self.client.get(reverse("orders:history")).status_code, 200)

        # The session expires server-side while the customer is checking out.
        Session.objects.all().delete()
        response = self.client.post(reverse("orders:place"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])
        self.assertEqual(Order.objects.count(), 0)
        cart_item = CartItem.objects.get(customer=customer)
        self.assertEqual(cart_item.quantity, 1)

        # Logging in again restores access and the order then succeeds.
        self.client.force_login(customer)
        again = self.client.post(reverse("orders:place"))
        self.assertRedirects(again, reverse("orders:history"))
        self.assertEqual(Order.objects.filter(customer=customer).count(), 1)
