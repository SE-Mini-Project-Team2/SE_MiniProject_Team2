"""Cross-module security tests owned by Security & Integration (M4).

SEC-CTRL-13  user-supplied content is output-escaped everywhere it is shown
SEC-CTRL-14  no raw SQL or unsafe-output constructs in application code
SEC-CTRL-17  hosted settings pass `manage.py check --deploy`
"""

import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from accounts.models import UserRole
from books.models import Book


User = get_user_model()
BASE_DIR = Path(settings.BASE_DIR)


# ---------------------------------------------------------------------------
# SEC-CTRL-17: deployment hardening
# ---------------------------------------------------------------------------


def run_manage(*args, env_overrides):
    """Run manage.py in a fresh interpreter so settings.py is re-evaluated
    with the given environment, exactly as a real deployment would load it."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("DJANGO_")}
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "manage.py", *args],
        cwd=BASE_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def production_env(**extra):
    env = {
        "DJANGO_DEBUG": "false",
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(50),
        "DJANGO_ALLOWED_HOSTS": "bookstore.example.com",
    }
    env.update(extra)
    return env


SETTINGS_PROBE = (
    "import json; from django.conf import settings as s; print(json.dumps({"
    "'DEBUG': s.DEBUG, 'ALLOWED_HOSTS': s.ALLOWED_HOSTS,"
    "'SESSION_COOKIE_SECURE': s.SESSION_COOKIE_SECURE,"
    "'SESSION_COOKIE_HTTPONLY': s.SESSION_COOKIE_HTTPONLY,"
    "'CSRF_COOKIE_SECURE': s.CSRF_COOKIE_SECURE,"
    "'CSRF_COOKIE_HTTPONLY': s.CSRF_COOKIE_HTTPONLY,"
    "'SECURE_SSL_REDIRECT': s.SECURE_SSL_REDIRECT,"
    "'SECURE_HSTS_SECONDS': s.SECURE_HSTS_SECONDS,"
    "'SECURE_HSTS_INCLUDE_SUBDOMAINS': s.SECURE_HSTS_INCLUDE_SUBDOMAINS,"
    "'SECURE_CONTENT_TYPE_NOSNIFF': s.SECURE_CONTENT_TYPE_NOSNIFF,"
    "'X_FRAME_OPTIONS': s.X_FRAME_OPTIONS}))"
)


class DeploymentSettingsTests(SimpleTestCase):
    def test_sec_ctrl_17_check_deploy_passes_in_production_mode(self):
        result = run_manage(
            "check", "--deploy", "--fail-level", "WARNING",
            env_overrides=production_env(),
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("System check identified no issues", result.stdout)

    def test_sec_ctrl_17_production_settings_values(self):
        result = run_manage(
            "shell", "-c", SETTINGS_PROBE, env_overrides=production_env()
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        values = json.loads(result.stdout.strip().splitlines()[-1])

        self.assertFalse(values["DEBUG"])
        self.assertEqual(values["ALLOWED_HOSTS"], ["bookstore.example.com"])
        self.assertTrue(values["SESSION_COOKIE_SECURE"])
        self.assertTrue(values["SESSION_COOKIE_HTTPONLY"])
        self.assertTrue(values["CSRF_COOKIE_SECURE"])
        self.assertTrue(values["CSRF_COOKIE_HTTPONLY"])
        self.assertTrue(values["SECURE_SSL_REDIRECT"])
        self.assertGreater(values["SECURE_HSTS_SECONDS"], 0)
        self.assertTrue(values["SECURE_HSTS_INCLUDE_SUBDOMAINS"])
        self.assertTrue(values["SECURE_CONTENT_TYPE_NOSNIFF"])
        self.assertEqual(values["X_FRAME_OPTIONS"], "DENY")

    def test_sec_ctrl_17_production_refuses_to_start_without_secret_key(self):
        env = production_env()
        del env["DJANGO_SECRET_KEY"]

        result = run_manage("check", env_overrides=env)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImproperlyConfigured", result.stderr)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_sec_ctrl_17_dev_defaults_are_flagged_by_check_deploy(self):
        # Proves the passing test above is meaningful: without production
        # environment variables, check --deploy must fail.
        result = run_manage(
            "check", "--deploy", "--fail-level", "WARNING", env_overrides={}
        )

        self.assertNotEqual(result.returncode, 0)
        output = result.stdout + result.stderr
        for warning in ("security.W008", "security.W012", "security.W016", "security.W018"):
            self.assertIn(warning, output)


# ---------------------------------------------------------------------------
# SEC-CTRL-13: output escaping of user-supplied content
# ---------------------------------------------------------------------------

SCRIPT = '<script>alert("xss")</script>'
SCRIPT_ESCAPED = "&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;"
IMG = "<img src=x onerror=alert(1)>"
IMG_ESCAPED = "&lt;img src=x onerror=alert(1)&gt;"
PASSWORD = "A-secure-unique-password-42"


class OutputEscapingTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user(
            email="xss-seller@example.com",
            password=PASSWORD,
            name="Seller",
            role=UserRole.SELLER,
        )
        self.customer = User.objects.create_user(
            email="xss-customer@example.com",
            password=PASSWORD,
            name="Customer",
            role=UserRole.CUSTOMER,
        )

    def _seller_posts_malicious_listing(self):
        self.client.force_login(self.seller)
        response = self.client.post(
            reverse("books:add"),
            {
                "title": SCRIPT,
                "author": IMG,
                "price": "199.00",
                "description": SCRIPT + IMG,
            },
        )
        self.assertRedirects(response, reverse("books:list"))
        self.client.logout()
        return Book.objects.get(seller=self.seller)

    def assertEscaped(self, response, *pairs):
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        for raw, escaped in pairs:
            self.assertNotIn(raw, content)
            self.assertIn(escaped, content)

    def test_sec_ctrl_13_script_in_listing_shown_as_text_on_book_list(self):
        book = self._seller_posts_malicious_listing()

        # Stored as submitted (escaping happens on output, not input).
        self.assertEqual(book.title, SCRIPT)

        response = self.client.get(reverse("books:list"))
        self.assertEscaped(response, (SCRIPT, SCRIPT_ESCAPED), (IMG, IMG_ESCAPED))

    def test_sec_ctrl_13_search_results_escape_listing_fields(self):
        self._seller_posts_malicious_listing()

        response = self.client.get(reverse("books:search"), {"q": "script"})
        self.assertEscaped(response, (SCRIPT, SCRIPT_ESCAPED), (IMG, IMG_ESCAPED))

    def test_sec_ctrl_13_search_text_is_escaped_when_echoed(self):
        breakout = '"><script>alert(1)</script>'
        self.client.force_login(self.seller)  # sellers also see "Add ... as a new book"

        response = self.client.get(reverse("books:search"), {"q": breakout})

        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("<script>alert(1)</script>", content)
        self.assertNotIn('value=""><script>', content)
        self.assertIn("&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;", content)

    def test_sec_ctrl_13_add_book_title_prefill_is_escaped(self):
        self.client.force_login(self.seller)

        response = self.client.get(reverse("books:add"), {"title": SCRIPT})

        self.assertEscaped(response, (SCRIPT, SCRIPT_ESCAPED))

    def test_sec_ctrl_13_cart_and_order_history_escape_book_fields(self):
        book = self._seller_posts_malicious_listing()
        self.client.force_login(self.customer)
        self.client.post(reverse("cart:add_to_cart", args=[book.pk]))

        cart = self.client.get(reverse("cart:view_cart"))
        self.assertEscaped(cart, (SCRIPT, SCRIPT_ESCAPED), (IMG, IMG_ESCAPED))

        self.client.post(reverse("orders:place"))
        history = self.client.get(reverse("orders:history"))
        self.assertEscaped(history, (SCRIPT, SCRIPT_ESCAPED))

    def test_sec_ctrl_13_user_name_is_escaped_on_home_page(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": SCRIPT,
                "email": "xss-name@example.com",
                "role": UserRole.CUSTOMER,
                "password1": PASSWORD,
                "password2": PASSWORD,
            },
        )
        self.assertRedirects(response, reverse("accounts:login"))
        self.client.force_login(User.objects.get(email="xss-name@example.com"))

        response = self.client.get(reverse("home"))
        self.assertEscaped(response, (SCRIPT, SCRIPT_ESCAPED))


# ---------------------------------------------------------------------------
# SEC-CTRL-13 / SEC-CTRL-14: static scan (the plan's "grep" verification)
# ---------------------------------------------------------------------------

UNSAFE_PATTERNS = {
    "|safe filter": re.compile(r"\|\s*safe\b"),
    "autoescape off": re.compile(r"\{%\s*autoescape\s+off"),
    "mark_safe()": re.compile(r"\bmark_safe\s*\("),
    "SafeString": re.compile(r"\bSafeString\b"),
    ".raw() query": re.compile(r"\.raw\s*\("),
    ".execute() SQL": re.compile(r"\.execute\s*\("),
    ".extra() query": re.compile(r"\.extra\s*\("),
    "RawSQL": re.compile(r"\bRawSQL\b"),
}
SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__", "migrations"}


def application_source_files():
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [
            d for d in dirs
            if d not in SKIP_DIRS and not (Path(root) / d / "pyvenv.cfg").exists()
        ]
        for name in files:
            if name == "tests.py" or name.startswith("test_"):
                continue  # test files mention these patterns on purpose
            if name.endswith((".py", ".html")):
                yield Path(root) / name


class UnsafeConstructScanTests(SimpleTestCase):
    def test_sec_ctrl_13_14_no_unsafe_output_or_raw_sql_in_app_code(self):
        files = list(application_source_files())
        self.assertGreater(len(files), 10, "scan found suspiciously few files")

        findings = []
        for path in files:
            text = path.read_text(encoding="utf-8", errors="replace")
            for lineno, line in enumerate(text.splitlines(), start=1):
                for label, pattern in UNSAFE_PATTERNS.items():
                    if pattern.search(line):
                        findings.append(
                            f"{path.relative_to(BASE_DIR)}:{lineno} {label}: {line.strip()}"
                        )

        self.assertEqual(findings, [], "\n".join(findings))
