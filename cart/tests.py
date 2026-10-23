from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from .models import CartItem

User = get_user_model()


class ShoppingCartTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer1",
            email="customer1@example.com",
            password="TestPass123!Secure",
            role="CUSTOMER",
        )
        self.other_customer = User.objects.create_user(
            username="customer2",
            email="customer2@example.com",
            password="TestPass456!Secure",
            role="CUSTOMER",
        )
        self.seller = User.objects.create_user(
            username="seller1",
            email="seller1@example.com",
            password="TestPass789!Secure",
            role="SELLER",
        )
        self.book = Book.objects.create(
            title="Python Basics",
            author="Test Author",
            price="250.00",
            seller=self.seller,
        )

    def test_add_book_to_cart(self):
        self.client.force_login(self.customer)

        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id])
        )

        self.assertRedirects(response, reverse("cart:view_cart"))
        item = CartItem.objects.get(
            customer=self.customer,
            book=self.book,
        )
        self.assertEqual(item.quantity, 1)

    def test_adding_same_book_increases_quantity(self):
        CartItem.objects.create(
            customer=self.customer,
            book=self.book,
            quantity=1,
        )
        self.client.force_login(self.customer)

        self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id])
        )

        item = CartItem.objects.get(
            customer=self.customer,
            book=self.book,
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.line_total, 500)

    def test_view_cart_shows_total(self):
        CartItem.objects.create(
            customer=self.customer,
            book=self.book,
            quantity=2,
        )
        self.client.force_login(self.customer)

        response = self.client.get(reverse("cart:view_cart"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Basics")
        self.assertEqual(response.context["total"], 500)

    def test_remove_book_from_cart(self):
        item = CartItem.objects.create(
            customer=self.customer,
            book=self.book,
            quantity=1,
        )
        self.client.force_login(self.customer)

        response = self.client.post(
            reverse("cart:remove_from_cart", args=[item.id])
        )

        self.assertRedirects(response, reverse("cart:view_cart"))
        self.assertFalse(CartItem.objects.filter(pk=item.id).exists())

    def test_customer_cannot_remove_another_customers_item(self):
        item = CartItem.objects.create(
            customer=self.other_customer,
            book=self.book,
            quantity=1,
        )
        self.client.force_login(self.customer)

        response = self.client.post(
            reverse("cart:remove_from_cart", args=[item.id])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=item.id).exists())

    def test_quantity_cannot_exceed_ten(self):
        CartItem.objects.create(
            customer=self.customer,
            book=self.book,
            quantity=10,
        )
        self.client.force_login(self.customer)

        self.client.post(
            reverse("cart:add_to_cart", args=[self.book.id])
        )

        item = CartItem.objects.get(
            customer=self.customer,
            book=self.book,
        )
        self.assertEqual(item.quantity, 10)
