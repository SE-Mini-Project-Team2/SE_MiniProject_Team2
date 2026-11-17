from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from cart.models import CartItem
from orders.models import Order
from orders.services import BookSoldError, place_order

User = get_user_model()


def make_user(name, role):
    return User.objects.create_user(
        username=name,
        email=f"{name}@example.com",
        password="TestPass123!Secure",
        role=role,
    )


class SoldBooksBase(TestCase):
    def setUp(self):
        self.seller = make_user("seller-a", "SELLER")
        self.other_seller = make_user("seller-b", "SELLER")
        self.alice = make_user("alice", "CUSTOMER")
        self.bob = make_user("bob", "CUSTOMER")
        self.sold = Book.objects.create(
            title="Sold Title", author="Au", price="100.00", seller=self.seller
        )
        self.free = Book.objects.create(
            title="Free Title", author="Au", price="200.00", seller=self.seller
        )
        self.foreign = Book.objects.create(
            title="Foreign Title", author="Au", price="300.00",
            seller=self.other_seller,
        )

    def buy(self, customer, book):
        CartItem.objects.create(customer=customer, book=book, quantity=1)
        return place_order(customer)


class SoldBooksHiddenTests(SoldBooksBase):
    def test_browse_hides_sold_books_and_keeps_available_ones(self):
        self.buy(self.alice, self.sold)

        response = self.client.get(reverse("books:list"))

        self.assertNotContains(response, "Sold Title")
        self.assertContains(response, "Free Title")

    def test_search_hides_sold_books(self):
        self.buy(self.alice, self.sold)

        response = self.client.get(reverse("books:search"), {"q": "Title"})

        self.assertNotContains(response, "Sold Title")
        self.assertContains(response, "Free Title")
        self.assertContains(response, "2 books found.")

    def test_search_for_only_sold_book_finds_nothing(self):
        self.buy(self.alice, self.sold)

        response = self.client.get(reverse("books:search"), {"q": "Sold"})

        self.assertContains(response, "No books found matching your search.")

    def test_unsold_book_stays_visible_after_other_book_sells(self):
        self.buy(self.alice, self.sold)

        self.assertFalse(Book.objects.get(pk=self.free.pk).is_sold)
        self.assertTrue(Book.objects.get(pk=self.sold.pk).is_sold)

    def test_sold_book_cannot_be_added_to_cart(self):
        self.buy(self.alice, self.sold)
        self.client.force_login(self.bob)

        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.sold.id]), follow=True
        )

        self.assertContains(response, "This book has already been sold.")
        self.assertFalse(CartItem.objects.filter(customer=self.bob).exists())

    def test_order_refused_if_book_sold_to_someone_else_first(self):
        CartItem.objects.create(customer=self.alice, book=self.sold, quantity=1)
        CartItem.objects.create(customer=self.bob, book=self.sold, quantity=1)
        CartItem.objects.create(customer=self.bob, book=self.free, quantity=1)
        place_order(self.alice)

        with self.assertRaises(BookSoldError) as raised:
            place_order(self.bob)

        self.assertEqual(raised.exception.titles, ["Sold Title"])
        self.assertFalse(Order.objects.filter(customer=self.bob).exists())
        self.assertEqual(CartItem.objects.filter(customer=self.bob).count(), 2)

    def test_checkout_page_shows_message_when_book_already_sold(self):
        CartItem.objects.create(customer=self.alice, book=self.sold, quantity=1)
        CartItem.objects.create(customer=self.bob, book=self.sold, quantity=1)
        place_order(self.alice)
        self.client.force_login(self.bob)

        response = self.client.post(reverse("orders:place"), follow=True)

        self.assertContains(response, "already sold to another customer")
        self.assertContains(response, "Sold Title")
        self.assertEqual(Order.objects.filter(customer=self.bob).count(), 0)


class SellerListingsTests(SoldBooksBase):
    def test_seller_sees_own_listings_with_status(self):
        self.buy(self.alice, self.sold)
        self.client.force_login(self.seller)

        response = self.client.get(reverse("books:my_listings"))

        self.assertContains(response, "Sold Title")
        self.assertContains(response, "Free Title")
        self.assertContains(response, ">Sold</span>")
        self.assertContains(response, ">Available</span>")

    def test_sold_book_shows_purchase_date(self):
        order = self.buy(self.alice, self.sold)
        self.client.force_login(self.seller)

        response = self.client.get(reverse("books:my_listings"))

        self.assertContains(response, order.created_at.strftime("%d %b %Y"))

    def test_listing_updates_when_a_customer_buys_it(self):
        self.client.force_login(self.seller)
        before = self.client.get(reverse("books:my_listings"))
        self.assertNotContains(before, ">Sold</span>")

        self.buy(self.alice, self.free)

        after = self.client.get(reverse("books:my_listings"))
        self.assertContains(after, ">Sold</span>")

    def test_seller_does_not_see_another_sellers_listings(self):
        self.client.force_login(self.seller)

        response = self.client.get(reverse("books:my_listings"))

        self.assertNotContains(response, "Foreign Title")

    def test_customer_cannot_open_my_listings(self):
        self.client.force_login(self.alice)

        response = self.client.get(reverse("books:my_listings"))

        self.assertEqual(response.status_code, 403)

    def test_anonymous_is_sent_to_login(self):
        response = self.client.get(reverse("books:my_listings"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response["Location"])

    def test_empty_state_for_seller_without_listings(self):
        newbie = make_user("newbie", "SELLER")
        self.client.force_login(newbie)

        response = self.client.get(reverse("books:my_listings"))

        self.assertContains(response, "You have not listed any books yet.")

    def test_seller_navigation_links_to_my_listings(self):
        self.client.force_login(self.seller)

        response = self.client.get(reverse("home"))

        self.assertContains(response, reverse("books:my_listings"))
