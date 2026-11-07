"""SEC-CTRL-19: generic error pages; stack traces are never exposed.

Verification from the Security & Integration Plan: trigger a 500 and a 404.
"""

from django.conf import settings
from django.http import HttpResponse
from django.test import Client, SimpleTestCase, override_settings
from django.urls import include, path

SECRET_DETAIL = "internal-detail-db-password-hunter2"


def boom(request):
    raise RuntimeError(SECRET_DETAIL)


def fine(request):
    return HttpResponse("ok")


urlpatterns = [
    path("boom/", boom),
    path("fine/", fine),
    path("", include("config.urls")),
]

LEAK_MARKERS = [
    "Traceback",
    "RuntimeError",
    SECRET_DETAIL,
    "test_error_pages.py",
    "/home/",
    "site-packages",
    "You're seeing this error because you have",
    "DEBUG = True",
]


@override_settings(ROOT_URLCONF=__name__, DEBUG=False)
class GenericErrorPageTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(raise_request_exception=False)

    def assertNoLeak(self, response):
        body = response.content.decode()
        for marker in LEAK_MARKERS + [settings.SECRET_KEY]:
            self.assertNotIn(marker, body)
        self.assertNotIn("Exception Value", body)

    def test_sec_ctrl_19_unknown_url_returns_generic_404(self):
        response = self.client.get("/no/such/page/")

        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)
        self.assertNoLeak(response)
        # The 404 must not echo the requested path back (no URL-list leak).
        self.assertNotContains(response, "/no/such/page/", status_code=404)
        self.assertNotContains(response, "URLconf", status_code=404)

    def test_sec_ctrl_19_server_error_returns_generic_500(self):
        response = self.client.get("/boom/")

        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Something went wrong", status_code=500)
        self.assertNoLeak(response)

    def test_sec_ctrl_19_post_that_crashes_also_returns_generic_500(self):
        response = self.client.post("/boom/")

        self.assertEqual(response.status_code, 500)
        self.assertNoLeak(response)

    def test_sec_ctrl_19_error_pages_link_back_home(self):
        for url in ("/no/such/page/", "/boom/"):
            with self.subTest(url=url):
                self.assertContains(
                    self.client.get(url),
                    'href="/"',
                    status_code=self.client.get(url).status_code,
                )

    def test_sec_ctrl_19_working_pages_are_unaffected(self):
        self.assertEqual(self.client.get("/fine/").status_code, 200)


@override_settings(ROOT_URLCONF=__name__, DEBUG=True)
class DebugModeControlTests(SimpleTestCase):
    def test_sec_ctrl_19_debug_true_would_leak_so_production_must_set_false(self):
        # Control case: proves the checks above can detect a leak.
        response = Client(raise_request_exception=False).get("/boom/")

        self.assertEqual(response.status_code, 500)
        self.assertIn(SECRET_DETAIL, response.content.decode())


class ProductionDebugDefaultTests(SimpleTestCase):
    def test_sec_ctrl_19_debug_is_off_under_the_test_runner(self):
        self.assertFalse(settings.DEBUG)
