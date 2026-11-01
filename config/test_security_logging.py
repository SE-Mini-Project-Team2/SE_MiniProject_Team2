"""SEC-CTRL-18: safe logging of security-relevant events.

Plan verification is a "log review"; these tests do that review automatically
by capturing every line written to the "security" logger.
"""

import logging
import re
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_login_failed
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from accounts.models import UserRole
from accounts.security_log import (
    RedactSecretsFilter,
    UTCFormatter,
    clean_value,
    email_reference,
    log_event,
)
from books.models import Book
from cart.models import CartItem

User = get_user_model()
PASSWORD = "A-secure-unique-password-42"
WRONG_PASSWORD = "Wr0ng-Guess-Password-77"


class SecurityLogTestCase(TestCase):
    def setUp(self):
        cache.clear()
        self.customer = User.objects.create_user(
            email="log-customer@example.com", password=PASSWORD,
            name="Customer", role=UserRole.CUSTOMER,
        )
        self.seller = User.objects.create_user(
            email="log-seller@example.com", password=PASSWORD,
            name="Seller", role=UserRole.SELLER,
        )

    def tearDown(self):
        cache.clear()

    def login_attempt(self, email, password, client=None):
        return (client or self.client).post(
            reverse("accounts:login"), {"email": email, "password": password}
        )

    def lines(self, captured):
        return [record.getMessage() for record in captured.records]


class FailedLoginLoggingTests(SecurityLogTestCase):
    def test_sec_ctrl_18_failed_login_for_known_user_logs_user_id(self):
        with self.assertLogs("security", "WARNING") as captured:
            self.login_attempt(self.customer.email, WRONG_PASSWORD)

        line = self.lines(captured)[0]
        self.assertIn("event=login_failed", line)
        self.assertIn(f"user_id={self.customer.pk} ", line)
        self.assertIn("ip=127.0.0.1", line)
        self.assertIn("path=/login/", line)

    def test_sec_ctrl_18_failed_login_for_unknown_email_logs_unknown_user(self):
        with self.assertLogs("security", "WARNING") as captured:
            self.login_attempt("nobody@example.com", WRONG_PASSWORD)

        line = self.lines(captured)[0]
        self.assertIn("event=login_failed", line)
        self.assertIn("user_id=unknown", line)
        self.assertIn(f"email_ref={email_reference('nobody@example.com')}", line)

    def test_sec_ctrl_18_lockout_is_logged(self):
        with override_settings(LOGIN_FAILURE_LIMIT=3):
            with self.assertLogs("security", "WARNING") as captured:
                for _ in range(3):
                    self.login_attempt(self.customer.email, WRONG_PASSWORD)
                self.login_attempt(self.customer.email, PASSWORD)

        events = [line.split()[0] for line in self.lines(captured)]
        self.assertEqual(events.count("event=login_failed"), 3)
        self.assertEqual(events[-1], "event=login_locked_out")
        self.assertIn(f"user_id={self.customer.pk} ", self.lines(captured)[-1])

    def test_sec_ctrl_18_successful_login_logs_no_security_event(self):
        with self.assertNoLogs("security", "WARNING"):
            self.login_attempt(self.customer.email, PASSWORD)


class AccessDeniedLoggingTests(SecurityLogTestCase):
    def test_sec_ctrl_18_anonymous_access_is_logged(self):
        with self.assertLogs("security", "WARNING") as captured:
            self.client.get(reverse("books:add"))

        line = self.lines(captured)[0]
        self.assertIn("event=access_denied", line)
        self.assertIn("user_id=anonymous", line)
        self.assertIn("reason=unauthenticated", line)
        self.assertIn("path=/books/add/", line)

    def test_sec_ctrl_18_wrong_role_is_logged_with_user_id(self):
        self.client.force_login(self.customer)

        with self.assertLogs("security", "WARNING") as captured:
            response = self.client.get(reverse("books:add"))

        self.assertEqual(response.status_code, 403)
        line = self.lines(captured)[0]
        self.assertIn("event=access_denied", line)
        self.assertIn(f"user_id={self.customer.pk} ", line)
        self.assertIn("reason=wrong_role", line)
        self.assertIn("required_role=SELLER", line)
        self.assertIn("actual_role=CUSTOMER", line)

    def test_sec_ctrl_18_query_string_is_not_logged(self):
        self.client.force_login(self.customer)

        with self.assertLogs("security", "WARNING") as captured:
            self.client.get(reverse("books:add") + "?token=abc123&title=x")

        line = self.lines(captured)[0]
        self.assertNotIn("abc123", line)
        self.assertNotIn("token", line)


class FailedOrderLoggingTests(SecurityLogTestCase):
    def setUp(self):
        super().setUp()
        self.book = Book.objects.create(
            title="Dune", author="Frank Herbert", price="499.00", seller=self.seller
        )
        self.client.force_login(self.customer)

    def test_sec_ctrl_18_empty_cart_order_is_logged(self):
        with self.assertLogs("security", "WARNING") as captured:
            self.client.post(reverse("orders:place"))

        line = self.lines(captured)[0]
        self.assertIn("event=order_failed", line)
        self.assertIn(f"user_id={self.customer.pk} ", line)
        self.assertIn("reason=empty_cart", line)

    def test_sec_ctrl_18_order_crash_is_logged_without_exception_message(self):
        CartItem.objects.create(customer=self.customer, book=self.book, quantity=1)
        secret = "db-connection-string-hunter2"
        client = Client(raise_request_exception=False)
        client.force_login(self.customer)

        with mock.patch(
            "orders.services.OrderItem.objects.bulk_create",
            side_effect=RuntimeError(secret),
        ):
            with self.assertLogs("security", "WARNING") as captured:
                response = client.post(reverse("orders:place"))

        self.assertEqual(response.status_code, 500)
        line = self.lines(captured)[0]
        self.assertIn("event=order_failed", line)
        self.assertIn("reason=error", line)
        self.assertIn("error=RuntimeError", line)
        self.assertNotIn(secret, line)


class SensitiveDataExclusionTests(SecurityLogTestCase):
    def test_sec_ctrl_18_logs_never_contain_passwords_emails_or_session_ids(self):
        client = Client()
        with self.assertLogs("security", "WARNING") as captured:
            self.login_attempt(self.customer.email, WRONG_PASSWORD, client)
            self.login_attempt("ghost@example.com", WRONG_PASSWORD, client)
            client.force_login(self.customer)
            client.get(reverse("books:add"))  # wrong role -> logged
            session_key = client.session.session_key
            csrf_cookie = client.cookies.get("csrftoken")

        everything = "\n".join(self.lines(captured))
        self.assertGreaterEqual(len(captured.records), 3)
        for secret in (
            WRONG_PASSWORD, PASSWORD, settings.SECRET_KEY, session_key,
            self.customer.email, "ghost@example.com", self.customer.password,
        ):
            self.assertNotIn(secret, everything)
        if csrf_cookie:
            self.assertNotIn(csrf_cookie.value, everything)

    def test_sec_ctrl_18_email_reference_is_stable_and_not_the_email(self):
        self.assertEqual(email_reference("A@B.com "), email_reference("a@b.com"))
        self.assertNotEqual(email_reference("a@b.com"), email_reference("c@d.com"))
        self.assertNotIn("a@b.com", email_reference("a@b.com"))
        self.assertEqual(len(email_reference("a@b.com")), 12)


class LogInjectionAndFormatTests(SecurityLogTestCase):
    def test_sec_ctrl_18_newlines_in_values_cannot_forge_log_lines(self):
        with self.assertLogs("security", "WARNING") as captured:
            log_event(
                "login_failed", user_id="1\nevent=fake_admin_login user_id=1",
                reason="x\r\n2026-01-01 INFO security event=forged",
            )
            user_login_failed.send(
                sender=None,
                credentials={"username": "evil\nevent=forged", "password": "pw"},
                request=None,
            )

        self.assertEqual(len(captured.records), 2)
        for line in self.lines(captured):
            self.assertNotRegex(line, r"[\r\n\t]")
            self.assertEqual(line.count("event="), 1)

    def test_sec_ctrl_18_clean_value_removes_control_characters_and_limits_length(self):
        self.assertEqual(clean_value("a b\nc\x00d"), "a_b_c_d")
        self.assertEqual(len(clean_value("x" * 1000)), 200)

    def test_sec_ctrl_18_log_lines_have_a_utc_timestamp(self):
        formatter = UTCFormatter(
            settings.LOGGING["formatters"]["security"]["format"]
        )
        with self.assertLogs("security", "WARNING") as captured:
            self.client.get(reverse("books:add"))

        text = formatter.format(captured.records[0])
        self.assertRegex(text, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} WARNING security event=access_denied")


class RedactionFilterTests(TestCase):
    def make_record(self, message):
        return logging.LogRecord("x", logging.INFO, "f.py", 1, message, (), None)

    def test_sec_ctrl_18_filter_masks_secret_looking_text(self):
        for message, leaked in [
            ("login password=Hunter2!x ok", "Hunter2!x"),
            ("cookie sessionid=abcd1234efgh done", "abcd1234efgh"),
            ("form csrfmiddlewaretoken=Zz9Yy8 sent", "Zz9Yy8"),
            ("Authorization: Bearer-token-123", "Bearer-token-123"),
            (f"key is {settings.SECRET_KEY} here", settings.SECRET_KEY),
        ]:
            with self.subTest(message=message):
                record = self.make_record(message)
                RedactSecretsFilter().filter(record)
                self.assertNotIn(leaked, record.getMessage())
                self.assertIn("[REDACTED]", record.getMessage())

    def test_sec_ctrl_18_filter_leaves_normal_events_unchanged(self):
        message = "event=login_failed user_id=7 ip=127.0.0.1 path=/login/"
        record = self.make_record(message)
        RedactSecretsFilter().filter(record)
        self.assertEqual(record.getMessage(), message)

    def test_sec_ctrl_18_security_logger_is_configured_with_the_filter(self):
        config = settings.LOGGING
        self.assertIn("security", config["loggers"])
        handler = config["handlers"]["console"]
        self.assertIn("redact_secrets", handler["filters"])
        self.assertFalse(config["loggers"]["security"]["propagate"])
        security = logging.getLogger("security")
        self.assertTrue(security.handlers)
        self.assertTrue(
            all(any(isinstance(f, RedactSecretsFilter) for f in h.filters)
                for h in security.handlers)
        )
