from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.utils import timezone

from accounts.models import User, UserRole
from books.models import Book
from cart.models import CartItem

from .models import Order
from .services import EmptyCartError, place_order


class PlaceOrderServiceTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="seller@test.com", password="Str0ngPass!9", role=UserRole.SELLER
        )
        self.customer = User.objects.create_user(
            email="cust@test.com", password="Str0ngPass!9", role=UserRole.CUSTOMER
        )
        self.book = Book.objects.create(
            title="Clean Code", author="Robert Martin",
            price=Decimal("499.00"), seller=self.seller,
        )

    def test_sec_ctrl_11_place_order_creates_order_and_clears_cart(self):
        CartItem.objects.create(customer=self.customer, book=self.book, quantity=2)

        order = place_order(self.customer)

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().unit_price, Decimal("499.00"))
        self.assertEqual(order.total, Decimal("998.00"))
        self.assertEqual(order.status, "Placed")
        self.assertEqual(CartItem.objects.filter(customer=self.customer).count(), 0)

    def test_empty_cart_raises_and_creates_nothing(self):
        with self.assertRaises(EmptyCartError):
            place_order(self.customer)
        self.assertEqual(Order.objects.count(), 0)

    def test_sec_ctrl_09_price_change_after_add_to_cart_uses_current_price(self):
        CartItem.objects.create(customer=self.customer, book=self.book, quantity=1)
        self.book.price = Decimal("599.00")
        self.book.save(update_fields=["price"])

        order = place_order(self.customer)

        self.assertEqual(order.items.first().unit_price, Decimal("599.00"))


class OrderViewTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="seller2@test.com", password="Str0ngPass!9", role=UserRole.SELLER
        )
        self.customer = User.objects.create_user(
            email="cust2@test.com", password="Str0ngPass!9", role=UserRole.CUSTOMER
        )
        self.book = Book.objects.create(
            title="Dune", author="Frank Herbert",
            price=Decimal("350.00"), seller=self.seller,
        )
        self.client = Client()

    def test_sec_ctrl_06_seller_cannot_place_order(self):
        self.client.login(email="seller2@test.com", password="Str0ngPass!9")
        response = self.client.post("/orders/place/")
        self.assertEqual(response.status_code, 403)

    def test_sec_ctrl_05_anonymous_redirected_to_login(self):
        response = self.client.post("/orders/place/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_it_03_place_order_then_view_history(self):
        self.client.login(email="cust2@test.com", password="Str0ngPass!9")
        CartItem.objects.create(customer=self.customer, book=self.book, quantity=1)

        self.client.post("/orders/place/")
        response = self.client.get("/orders/")
        order = Order.objects.get(customer=self.customer)

        self.assertContains(response, f"Order #{order.pk}")
        self.assertContains(
            response,
            order.created_at.strftime("%d %b %Y %H:%M"),
        )
        self.assertContains(response, "Status: Placed")
        self.assertContains(response, "Dune")
        self.assertContains(response, str(order.total))
        self.assertEqual(CartItem.objects.filter(customer=self.customer).count(), 0)

    def test_order_history_displays_newest_orders_first(self):
        later_order_book = Book.objects.create(
            title="Later Order Book", author="Test Author",
            price=Decimal("100.00"), seller=self.seller,
        )
        CartItem.objects.create(customer=self.customer, book=self.book, quantity=1)
        earlier_order = place_order(self.customer)
        CartItem.objects.create(
            customer=self.customer, book=later_order_book, quantity=1,
        )
        place_order(self.customer)
        Order.objects.filter(pk=earlier_order.pk).update(
            created_at=timezone.now() - timedelta(days=1),
        )

        self.client.force_login(self.customer)
        response = self.client.get("/orders/")

        self.assertLess(
            response.content.index(b"Later Order Book"),
            response.content.index(b"Dune"),
        )

    def test_empty_order_history_displays_message(self):
        self.client.force_login(self.customer)

        response = self.client.get("/orders/")

        self.assertContains(response, "You have not placed any orders yet.")

    def test_sec_ctrl_05_anonymous_cannot_view_order_history(self):
        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_sec_ctrl_06_seller_cannot_view_order_history(self):
        self.client.force_login(self.seller)

        response = self.client.get("/orders/")

        self.assertEqual(response.status_code, 403)

    # TC-15 assumes an order-detail route; the current design only exposes
    # this customer-scoped history list.
    def test_sec_ctrl_08_customer_only_sees_own_orders(self):
        other = User.objects.create_user(
            email="other@test.com", password="Str0ngPass!9", role=UserRole.CUSTOMER
        )
        CartItem.objects.create(customer=other, book=self.book, quantity=1)
        place_order(other)

        self.client.login(email="cust2@test.com", password="Str0ngPass!9")
        response = self.client.get("/orders/")

        self.assertNotContains(response, "Dune")
