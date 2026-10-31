from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from unittest import mock

from .decorators import role_required
from .models import UserRole


User = get_user_model()


class RegistrationTests(TestCase):
    def test_customer_can_register(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "A Customer",
                "email": "customer@example.com",
                "role": UserRole.CUSTOMER,
                "password1": "A-secure-unique-password-42",
                "password2": "A-secure-unique-password-42",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        user = User.objects.get(email="customer@example.com")
        self.assertEqual(user.name, "A Customer")
        self.assertEqual(user.role, UserRole.CUSTOMER)
        self.assertNotEqual(user.password, "A-secure-unique-password-42")
        self.assertTrue(user.check_password("A-secure-unique-password-42"))

    def test_seller_can_register_with_only_allowed_role(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "A Seller",
                "email": "seller@example.com",
                "role": UserRole.SELLER,
                "password1": "A-secure-unique-password-42",
                "password2": "A-secure-unique-password-42",
            },
        )

        self.assertRedirects(response, reverse("accounts:login"))
        self.assertEqual(
            User.objects.get(email="seller@example.com").role,
            UserRole.SELLER,
        )

    def test_registration_rejects_missing_and_invalid_fields(self):
        invalid_data = [
            {},
            {
                "name": "A Customer",
                "email": "not-an-email",
                "role": UserRole.CUSTOMER,
                "password1": "A-secure-unique-password-42",
                "password2": "A-secure-unique-password-42",
            },
            {
                "name": "A Customer",
                "email": "customer@example.com",
                "role": "ADMIN",
                "password1": "A-secure-unique-password-42",
                "password2": "A-secure-unique-password-42",
            },
            {
                "name": "A Customer",
                "email": "customer@example.com",
                "role": UserRole.CUSTOMER,
                "password1": "short",
                "password2": "short",
            },
            {
                "name": "A Customer",
                "email": "customer@example.com",
                "role": UserRole.CUSTOMER,
                "password1": "12345678",
                "password2": "12345678",
            },
        ]

        for data in invalid_data:
            with self.subTest(data=data):
                response = self.client.post(
                    reverse("accounts:register"),
                    data,
                )
                self.assertEqual(response.status_code, 200)
                self.assertFalse(User.objects.exists())

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(
            email="customer@example.com",
            password="A-secure-unique-password-42",
            name="Existing Customer",
        )

        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "Duplicate",
                "email": "CUSTOMER@example.com",
                "role": UserRole.CUSTOMER,
                "password1": "A-secure-unique-password-42",
                "password2": "A-secure-unique-password-42",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertIn("email", response.context["form"].errors)


class LoginTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="book-test-user",
            email="bookuser@example.com",
            password="A-secure-unique-password-42",
            role=UserRole.SELLER,
        )

    def test_user_manager_supports_books_pr_fixture_interface(self):
        self.assertEqual(self.user.name, "book-test-user")
        self.assertEqual(self.user.role, "SELLER")

    def test_registered_email_and_password_create_a_session(self):
        session = self.client.session
        session["pre_login_value"] = "preserved"
        session.save()
        old_key = session.session_key

        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": self.user.email,
                "password": "A-secure-unique-password-42",
            },
        )

        self.assertRedirects(response, reverse("home"))
        self.assertNotEqual(self.client.session.session_key, old_key)
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        self.assertEqual(
            self.client.session["_auth_user_id"],
            str(self.user.pk),
        )

    def test_registration_and_login_normalize_email_case(self):
        password = "A-secure-unique-password-42"
        registration_response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "Alice",
                "email": "Alice@example.com",
                "role": UserRole.CUSTOMER,
                "password1": password,
                "password2": password,
            },
        )

        self.assertRedirects(
            registration_response,
            reverse("accounts:login"),
        )
        user = User.objects.get(email="alice@example.com")

        uppercase_login = self.client.post(
            reverse("accounts:login"),
            {"email": "Alice@example.com", "password": password},
        )
        self.assertRedirects(uppercase_login, reverse("home"))
        self.assertEqual(
            self.client.session["_auth_user_id"],
            str(user.pk),
        )

        self.client.post(reverse("accounts:logout"))
        lowercase_login = self.client.post(
            reverse("accounts:login"),
            {"email": "alice@example.com", "password": password},
        )
        self.assertRedirects(lowercase_login, reverse("home"))

    def test_invalid_credentials_have_the_same_generic_message(self):
        unknown_email = self.client.post(
            reverse("accounts:login"),
            {"email": "unknown@example.com", "password": "wrong"},
        )
        wrong_password = self.client.post(
            reverse("accounts:login"),
            {"email": self.user.email, "password": "wrong"},
        )

        self.assertEqual(unknown_email.status_code, 200)
        self.assertEqual(wrong_password.status_code, 200)
        self.assertEqual(
            unknown_email.context["form"].non_field_errors(),
            wrong_password.context["form"].non_field_errors(),
        )
        self.assertTrue(
            any(
                error.startswith(
                    "Please enter a correct email and password."
                )
                for error in unknown_email.context["form"].non_field_errors()
            )
        )

    def test_external_next_url_is_ignored(self):
        response = self.client.post(
            reverse("accounts:login") + "?next=https://evil.example/",
            {
                "email": self.user.email,
                "password": "A-secure-unique-password-42",
                "next": "https://evil.example/",
            },
        )

        self.assertRedirects(response, reverse("home"))

    def test_safe_next_url_is_followed(self):
        response = self.client.post(
            reverse("accounts:login") + "?next=/books/",
            {
                "email": self.user.email,
                "password": "A-secure-unique-password-42",
                "next": "/books/",
            },
        )

        self.assertRedirects(response, "/books/", fetch_redirect_response=False)


class LogoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="logout@example.com",
            password="A-secure-unique-password-42",
            name="Logout User",
        )
        self.client.force_login(self.user)

    def test_logout_requires_post(self):
        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)

    def test_logout_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_cannot_post_logout(self):
        response = Client().post(reverse("accounts:logout"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:logout')}",
        )

    def test_post_logout_destroys_session(self):
        old_key = self.client.session.session_key

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("home"))
        self.assertFalse(Session.objects.filter(session_key=old_key).exists())
        self.assertNotIn("_auth_user_id", self.client.session)

        old_session_client = Client()
        old_session_client.cookies["sessionid"] = old_key
        old_session_response = old_session_client.post(
            reverse("accounts:logout")
        )
        self.assertRedirects(
            old_session_response,
            f"{reverse('accounts:login')}?next={reverse('accounts:logout')}",
        )
        self.assertFalse(
            Session.objects.filter(session_key=old_key).exists()
        )


class RoleRequiredTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            email="role@example.com",
            password="A-secure-unique-password-42",
            name="Role Test User",
            role=UserRole.CUSTOMER,
        )

    def test_anonymous_user_is_redirected_to_login(self):
        @role_required(UserRole.SELLER)
        def protected_view(request):
            return None

        request = self.factory.get("/books/add/")
        request.user = AnonymousUser()

        response = protected_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("accounts:login")))

    def test_authenticated_user_with_wrong_role_gets_forbidden(self):
        @role_required(UserRole.SELLER)
        def protected_view(request):
            return None

        request = self.factory.get("/books/add/")
        request.user = self.user
        SessionMiddleware(lambda current_request: None).process_request(
            request
        )
        request.session.save()
        request._messages = FallbackStorage(request)

        response = protected_view(request)

        self.assertEqual(response.status_code, 403)


LOCKOUT_MESSAGE = "Too many failed login attempts. Please try again later."


@override_settings(LOGIN_FAILURE_LIMIT=5, LOGIN_LOCKOUT_SECONDS=900)
class LoginThrottlingTests(TestCase):
    """SEC-CTRL-16: five consecutive failures lock the email/IP pair."""

    password = "A-secure-unique-password-42"

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            email="throttle@example.com",
            password=self.password,
            name="Throttle Target",
            role=UserRole.CUSTOMER,
        )

    def tearDown(self):
        cache.clear()

    def _login(self, email, password, client=None):
        return (client or self.client).post(
            reverse("accounts:login"),
            {"email": email, "password": password},
        )

    def _fail(self, times, email=None):
        for _ in range(times):
            response = self._login(email or self.user.email, "wrong-password")
            self.assertEqual(response.status_code, 200)
            self.assertNotIn("_auth_user_id", self.client.session)

    def test_sec_ctrl_16_sixth_attempt_after_five_failures_is_locked_out(self):
        self._fail(5)

        # Sixth attempt uses the CORRECT password and must still be refused.
        response = self._login(self.user.email, self.password)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertIn(LOCKOUT_MESSAGE, response.context["form"].non_field_errors())

    def test_sec_ctrl_16_four_failures_do_not_lock_out(self):
        self._fail(4)

        response = self._login(self.user.email, self.password)

        self.assertRedirects(response, reverse("home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.user.pk)

    def test_sec_ctrl_16_successful_login_resets_failure_count(self):
        self._fail(4)
        self.assertRedirects(self._login(self.user.email, self.password), reverse("home"))
        self.client.post(reverse("accounts:logout"))

        # Without the reset this would be failure 8 and lock the account.
        self._fail(4)
        response = self._login(self.user.email, self.password)

        self.assertRedirects(response, reverse("home"))

    def test_sec_ctrl_16_lockout_message_does_not_reveal_unknown_email(self):
        self._fail(5, email="nobody@example.com")
        unknown = self._login("nobody@example.com", "anything")

        self._fail(5)
        known = self._login(self.user.email, "anything")

        self.assertEqual(
            unknown.context["form"].non_field_errors(),
            known.context["form"].non_field_errors(),
        )
        self.assertIn(LOCKOUT_MESSAGE, unknown.context["form"].non_field_errors())

    def test_sec_ctrl_16_lockout_does_not_block_other_accounts(self):
        other = User.objects.create_user(
            email="other@example.com",
            password=self.password,
            role=UserRole.CUSTOMER,
        )
        self._fail(5)

        response = self._login(other.email, self.password)

        self.assertRedirects(response, reverse("home"))

    def test_sec_ctrl_16_lockout_ignores_email_case(self):
        self._fail(5, email="THROTTLE@Example.com")

        response = self._login(self.user.email, self.password)

        self.assertIn(LOCKOUT_MESSAGE, response.context["form"].non_field_errors())

    def test_sec_ctrl_16_lockout_expires_after_lockout_window(self):
        import time as real_time

        from django.core.cache import caches

        if "locmem" not in type(caches["default"]).__module__:
            self.skipTest("fakes the clock of the local-memory cache backend")

        self._fail(5)
        self.assertIn(
            LOCKOUT_MESSAGE,
            self._login(self.user.email, self.password).context["form"].non_field_errors(),
        )

        future = real_time.time() + 901
        with mock.patch("django.core.cache.backends.locmem.time") as fake_time:
            fake_time.time.return_value = future
            response = self._login(self.user.email, self.password)

        self.assertRedirects(response, reverse("home"))

