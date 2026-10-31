"""NFR-06: the application stays split into accounts, books, cart and orders.

Each test maps to one acceptance criterion of issue #17 (NFR-06, SEC-CTRL-14).
They read the source with the `ast` module, so they fail the moment someone
adds an import or a query that breaks the module boundaries.
"""

import ast
import os
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.test import SimpleTestCase
from django.urls import resolve, reverse


BASE_DIR = Path(settings.BASE_DIR)
APP_NAMES = ["accounts", "books", "cart", "orders"]

# Which other project apps each app's production code may import.
# accounts is the base layer; orders sits on top. Arrows only point downward,
# so a change in a lower module never needs a change in a higher one.
ALLOWED_DEPENDENCIES = {
    "accounts": set(),
    "books": {"accounts"},
    "cart": {"accounts", "books"},
    "orders": {"accounts", "cart"},
}

SKIP_PARTS = {"migrations", "__pycache__", "tests", "templates"}


def production_files(app_name):
    """Python files of an app, without tests and migrations."""
    for path in sorted((BASE_DIR / app_name).rglob("*.py")):
        relative = path.relative_to(BASE_DIR / app_name)
        if set(relative.parts) & SKIP_PARTS:
            continue
        if path.name == "tests.py" or path.name.startswith("test_"):
            continue
        yield path


def parse(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def imported_project_apps(tree):
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            top = name.split(".")[0]
            if top in APP_NAMES:
                found.add(top)
    return found


class ModuleSeparationTests(SimpleTestCase):
    """Criterion 1: accounts, books, cart and orders are separate modules."""

    def test_nfr_06_all_four_modules_are_installed_django_apps(self):
        installed = {config.name for config in apps.get_app_configs()}
        self.assertTrue(set(APP_NAMES) <= installed, installed)

    def test_nfr_06_each_module_has_its_own_models_views_urls_and_tests(self):
        for name in APP_NAMES:
            for filename in ("models.py", "views.py", "urls.py"):
                with self.subTest(app=name, file=filename):
                    self.assertTrue((BASE_DIR / name / filename).is_file())
            with self.subTest(app=name, file="tests"):
                has_tests = (BASE_DIR / name / "tests.py").is_file() or any(
                    (BASE_DIR / name).glob("test_*.py")
                )
                self.assertTrue(has_tests)

    def test_nfr_06_each_module_owns_its_own_models(self):
        expected = {
            "accounts": {"User"},
            "books": {"Book"},
            "cart": {"CartItem"},
            "orders": {"Order", "OrderItem"},
        }
        for name, model_names in expected.items():
            with self.subTest(app=name):
                owned = {m.__name__ for m in apps.get_app_config(name).get_models()}
                self.assertEqual(owned, model_names)

    def test_nfr_06_each_module_is_routed_from_the_project_urls(self):
        # Resolve one real URL per module so a missing include() fails here.
        self.assertEqual(resolve(reverse("accounts:login")).app_name, "accounts")
        self.assertEqual(resolve(reverse("books:list")).app_name, "books")
        self.assertEqual(resolve(reverse("cart:view_cart")).app_name, "cart")
        self.assertEqual(resolve(reverse("orders:history")).app_name, "orders")

    def test_nfr_06_modules_only_depend_on_modules_below_them(self):
        # Criterion 4: a change in one area does not ripple into unrelated ones.
        violations = []
        for name in APP_NAMES:
            for path in production_files(name):
                used = imported_project_apps(parse(path)) - {name}
                extra = used - ALLOWED_DEPENDENCIES[name]
                if extra:
                    violations.append(
                        f"{path.relative_to(BASE_DIR)} imports {sorted(extra)}; "
                        f"{name} may only import {sorted(ALLOWED_DEPENDENCIES[name])}"
                    )
        self.assertEqual(violations, [], "\n".join(violations))

    def test_nfr_06_accounts_does_not_import_any_other_module(self):
        for path in production_files("accounts"):
            with self.subTest(file=path.name):
                self.assertEqual(
                    imported_project_apps(parse(path)) - {"accounts"}, set()
                )

    def test_nfr_06_project_package_only_wires_modules_together(self):
        # config may reference modules in urls/settings, but must hold no models.
        self.assertFalse((BASE_DIR / "config" / "models.py").exists())


class RoleChecksLiveInAccountsTests(SimpleTestCase):
    """Criterion 3: role checks come from accounts and are reused."""

    def test_nfr_06_role_required_is_defined_only_in_accounts(self):
        definitions = []
        for name in APP_NAMES:
            for path in production_files(name):
                for node in ast.walk(parse(path)):
                    if isinstance(node, ast.FunctionDef) and node.name == "role_required":
                        definitions.append(str(path.relative_to(BASE_DIR)))
        self.assertEqual(definitions, ["accounts/decorators.py"])

    def test_nfr_06_other_modules_reuse_accounts_role_required(self):
        for name in ("books", "cart", "orders"):
            with self.subTest(app=name):
                imports_it = any(
                    isinstance(node, ast.ImportFrom)
                    and node.module == "accounts.decorators"
                    and any(a.name == "role_required" for a in node.names)
                    for node in ast.walk(parse(BASE_DIR / name / "views.py"))
                )
                self.assertTrue(imports_it, f"{name}/views.py must import role_required")

    def test_nfr_06_no_hand_rolled_role_checks_outside_accounts(self):
        offenders = []
        for name in ("books", "cart", "orders"):
            for path in production_files(name):
                for node in ast.walk(parse(path)):
                    if isinstance(node, ast.Attribute) and node.attr in {
                        "role", "is_staff", "is_superuser",
                    }:
                        offenders.append(f"{path.relative_to(BASE_DIR)}:{node.lineno} .{node.attr}")
        self.assertEqual(offenders, [], "\n".join(offenders))


class OrmOnlyTests(SimpleTestCase):
    """Criterion 2 / SEC-CTRL-14: database access goes through the ORM."""

    FORBIDDEN_ATTRS = {"raw", "extra", "execute", "executemany", "cursor"}
    FORBIDDEN_NAMES = {"RawSQL"}

    def test_nfr_06_no_raw_sql_or_database_cursors_in_application_code(self):
        offenders = []
        for name in APP_NAMES + ["config"]:
            for path in production_files(name):
                for node in ast.walk(parse(path)):
                    if isinstance(node, ast.Attribute) and node.attr in self.FORBIDDEN_ATTRS:
                        offenders.append(f"{path.relative_to(BASE_DIR)}:{node.lineno} .{node.attr}")
                    if isinstance(node, ast.Name) and node.id in self.FORBIDDEN_NAMES:
                        offenders.append(f"{path.relative_to(BASE_DIR)}:{node.lineno} {node.id}")
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        modules = (
                            [a.name for a in node.names]
                            if isinstance(node, ast.Import)
                            else [node.module or ""]
                        )
                        if any(m.split(".")[0] in {"sqlite3", "psycopg2", "MySQLdb"} for m in modules):
                            offenders.append(f"{path.relative_to(BASE_DIR)}:{node.lineno} direct DB driver import")
        self.assertEqual(offenders, [], "\n".join(offenders))

    def test_nfr_06_scan_actually_sees_the_application_files(self):
        # Guards against the scans above silently passing on zero files.
        for name in APP_NAMES:
            self.assertGreaterEqual(len(list(production_files(name))), 4, name)
