from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from books.models import Book
from cart.models import CartItem
from orders.models import Order

User = get_user_model()


class NFR02NavigationAndFeedbackTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer = User.objects.create_user(
            username="nfr02_customer",
            email="nfr02_customer@example.com",
            password="A-secure-unique-password-42",
            role="CUSTOMER",
        )
        cls.seller = User.objects.create_user(
            username="nfr02_seller",
            email="nfr02_seller@example.com",
            password="A-secure-unique-password-42",
            role="SELLER",
        )
        cls.book = Book.objects.create(
            title="NFR Navigation",
            author="Test Author",
            price="25.00",
            seller=cls.seller,
        )

    def test_nfr02_major_operations_are_reachable_within_three_clicks(self):
        # Login: home -> Log In -> submit the login form (2 clicks).
        home = self.client.get(reverse("home"))
        self.assertContains(
            home,
            f'href="{reverse("accounts:login")}"',
        )
        login_page = self.client.get(reverse("accounts:login"))
        self.assertContains(login_page, '<button type="submit">Log in</button>')
        login_response = self.client.post(
            reverse("accounts:login"),
            {
                "email": self.customer.email,
                "password": "A-secure-unique-password-42",
            },
            follow=True,
        )
        self.assertRedirects(login_response, reverse("home"))
        self.assertContains(login_response, "You have been logged in.")

        # Search: submit the search form on home (1 click).
        home = self.client.get(reverse("home"))
        self.assertContains(
            home,
            f'action="{reverse("books:search")}"',
        )
        self.assertContains(
            home,
            f'href="{reverse("books:list")}"',
        )
        self.assertContains(home, "Search Books</button>")
        search = self.client.get(
            reverse("books:search"),
            {"q": self.book.title},
        )
        self.assertContains(search, self.book.title)

        # Cart: home -> Browse Books -> Add to Cart (2 clicks).
        book_list = self.client.get(reverse("books:list"))
        self.assertContains(
            book_list,
            f'action="{reverse("cart:add_to_cart", args=[self.book.pk])}"',
        )
        self.assertContains(book_list, "Add to Cart</button>")
        cart_response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.pk]),
            follow=True,
        )
        self.assertContains(cart_response, "Book added to your cart.")

        # Order with a populated cart: home -> My Cart -> Place Order (2 clicks).
        home = self.client.get(reverse("home"))
        self.assertContains(
            home,
            f'href="{reverse("cart:view_cart")}"',
        )
        cart = self.client.get(reverse("cart:view_cart"))
        self.assertContains(
            cart,
            f'action="{reverse("orders:place")}"',
        )
        self.assertContains(cart, "Place Order</button>")
        order_response = self.client.post(
            reverse("orders:place"),
            follow=True,
        )
        self.assertContains(order_response, "placed successfully.")

    def test_nfr02_navigation_and_actions_respect_user_roles(self):
        anonymous_home = self.client.get(reverse("home"))
        self.assertContains(
            anonymous_home,
            f'href="{reverse("accounts:login")}"',
        )
        self.assertContains(
            anonymous_home,
            f'href="{reverse("accounts:register")}"',
        )
        self.assertNotContains(anonymous_home, "My Cart")
        self.assertNotContains(anonymous_home, "My Orders")

        self.client.force_login(self.customer)
        customer_home = self.client.get(reverse("home"))
        self.assertContains(customer_home, "My Cart")
        self.assertContains(customer_home, "My Orders")
        self.assertNotContains(customer_home, "Add a Book Listing")
        customer_books = self.client.get(reverse("books:list"))
        self.assertContains(customer_books, "Add to Cart")
        self.assertNotContains(customer_books, "Add a Book Listing")

        self.client.force_login(self.seller)
        seller_home = self.client.get(reverse("home"))
        self.assertContains(seller_home, "Add a Book Listing")
        self.assertNotContains(seller_home, "My Cart")
        self.assertNotContains(seller_home, "My Orders")
        seller_books = self.client.get(reverse("books:list"))
        self.assertNotContains(seller_books, "Add to Cart")
        forbidden_cart = self.client.get(reverse("cart:view_cart"))
        self.assertContains(
            forbidden_cart,
            "You do not have permission to access this page.",
            status_code=403,
        )
        self.assertContains(
            forbidden_cart,
            "Add a Book Listing",
            status_code=403,
        )
        forbidden_orders = self.client.get(reverse("orders:history"))
        self.assertContains(
            forbidden_orders,
            "You do not have permission to access this page.",
            status_code=403,
        )

    def test_nfr02_search_shows_result_and_empty_result_feedback(self):
        results = self.client.get(
            reverse("books:search"),
            {"q": self.book.title},
        )
        self.assertContains(results, self.book.title)
        self.assertContains(results, "1 book found.")
        self.assertEqual(
            results.content.count(b"1 book found."),
            1,
        )
        self.assertEqual(
            results.content.count(b'class="message success"'),
            1,
        )

        empty_results = self.client.get(
            reverse("books:search"),
            {"q": "No matching title"},
        )
        self.assertContains(
            empty_results,
            "No books found matching your search.",
        )
        self.assertEqual(
            empty_results.content.count(
                b"No books found matching your search."
            ),
            1,
        )
        self.assertEqual(
            empty_results.content.count(b'class="message info"'),
            1,
        )

        invalid_query = self.client.get(
            reverse("books:search"),
            {"q": "x" * 101},
        )
        self.assertContains(
            invalid_query,
            "Search text must not exceed 100 characters.",
            status_code=400,
        )
        self.assertEqual(
            invalid_query.content.count(
                b"Search text must not exceed 100 characters."
            ),
            1,
        )
        self.assertNotContains(
            invalid_query,
            "No books found matching your search.",
            status_code=400,
        )

    def test_nfr02_registration_login_and_logout_show_success_feedback(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "New Customer",
                "email": "new_nfr02@example.com",
                "role": "CUSTOMER",
                "password1": "A-secure-unique-password-42",
                "password2": "A-secure-unique-password-42",
            },
            follow=True,
        )
        self.assertContains(
            response,
            "Your account was created. You can now log in.",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "new_nfr02@example.com",
                "password": "A-secure-unique-password-42",
            },
            follow=True,
        )
        self.assertContains(response, "You have been logged in.")

        response = self.client.post(
            reverse("accounts:logout"),
            follow=True,
        )
        self.assertContains(response, "You have been logged out.")

    def test_nfr02_invalid_registration_and_login_show_error_feedback(self):
        registration = self.client.post(
            reverse("accounts:register"),
            {},
        )
        self.assertContains(
            registration,
            "Please correct the errors below to create your account.",
        )
        self.assertContains(registration, 'role="alert"')
        self.assertContains(registration, "This field is required.")

        login = self.client.post(
            reverse("accounts:login"),
            {"email": self.customer.email, "password": "incorrect"},
        )
        self.assertContains(
            login,
            "Unable to log in. Check your email and password and try again.",
        )
        self.assertContains(login, "Please enter a correct email and password.")
        self.assertContains(login, 'role="alert"')

    def test_nfr02_book_and_cart_operations_show_success_and_error_feedback(
        self,
    ):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": "New NFR02 Book",
                "author": "Another Author",
                "price": "30.00",
                "description": "A new listing.",
            },
            follow=True,
        )
        self.assertContains(response, "Book listing added successfully.")

        invalid_book = self.client.post(
            reverse("books:add"),
            {"title": "", "author": "", "price": ""},
        )
        self.assertContains(
            invalid_book,
            "Please correct the errors below to add this book.",
        )
        self.assertContains(invalid_book, 'role="alert"')

        self.client.force_login(self.customer)
        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.pk]),
            follow=True,
        )
        self.assertContains(response, "Book added to your cart.")

        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.pk]),
            follow=True,
        )
        self.assertContains(response, "Cart quantity updated.")

        item = CartItem.objects.get(
            customer=self.customer,
            book=self.book,
        )
        response = self.client.post(
            reverse("cart:remove_from_cart", args=[item.pk]),
            follow=True,
        )
        self.assertContains(response, "Book removed from your cart.")

        CartItem.objects.create(
            customer=self.customer,
            book=self.book,
            quantity=10,
        )
        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.pk]),
            follow=True,
        )
        self.assertContains(
            response,
            "You can add a maximum of 10 copies of a book.",
        )
        self.assertContains(response, 'role="alert"')

    def test_nfr02_order_placement_shows_success_and_empty_cart_error(self):
        self.client.force_login(self.customer)
        response = self.client.post(
            reverse("orders:place"),
            follow=True,
        )
        self.assertContains(response, "Your cart is empty.")
        self.assertContains(response, 'role="alert"')

        CartItem.objects.create(
            customer=self.customer,
            book=self.book,
            quantity=1,
        )
        response = self.client.post(
            reverse("orders:place"),
            follow=True,
        )
        self.assertContains(response, "placed successfully.")
        self.assertEqual(Order.objects.filter(customer=self.customer).count(), 1)

    def test_tc17_nfr02_login_search_cart_and_order_workflow(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": self.customer.email,
                "password": "A-secure-unique-password-42",
            },
            follow=True,
        )
        self.assertContains(response, "You have been logged in.")

        search = self.client.get(
            reverse("books:search"),
            {"q": self.book.title},
        )
        self.assertContains(search, self.book.title)
        self.assertContains(search, "1 book found.")

        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.pk]),
            follow=True,
        )
        self.assertContains(response, "Book added to your cart.")

        response = self.client.post(
            reverse("cart:add_to_cart", args=[self.book.pk]),
            follow=True,
        )
        self.assertContains(response, "Cart quantity updated.")
        self.assertContains(response, "Quantity")

        response = self.client.post(
            reverse("orders:place"),
            follow=True,
        )
        self.assertContains(response, "placed successfully.")
        self.assertContains(response, "My Orders")
        self.assertEqual(Order.objects.filter(customer=self.customer).count(), 1)
