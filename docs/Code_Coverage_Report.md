# Code (Line) Coverage Report

**Project:** Online Bookstore (Django)  
**Reporter:** Ojas Binjola (M4, Security & Integration)  
**Measured on:** `main` at commit `6b7ad27` (after PRs #42 and #43), 2026-11-08  
**Tool:** Coverage.py 7.16.2, Django 5.2  
**Test run:** `python manage.py test` — 133 tests, all passed (OK)  

## 1. Result

| Measure | Covered | Total | Percentage |
|---|---|---|---|
| **Line (statement) coverage** | 490 | 625 | **78.4%** |

Coverage.py's combined figure (lines and branches together) is 76.1%. Branch coverage is reported separately in `Branch_Coverage_Report.md`.

## 2. How it was measured

```
pip install coverage
coverage erase
coverage run --branch --source=. --omit="*/tests.py,*/test_*.py,*/migrations/*,manage.py" manage.py test
coverage report --show-missing
coverage html -d docs/coverage
```

**What is measured:** all application source in `accounts`, `books`, `cart`, `orders` and `config`, plus `locustfile.py`.  
**What is excluded:** test files (`tests.py`, `test_*.py`), auto-generated `migrations/`, and `manage.py`.  
**Not captured by the tool:** four deployment-settings tests start a separate Python process with production environment variables (they run `manage.py check --deploy` and read the settings). Their behaviour is tested, but Coverage.py does not see code executed in that child process, so the matching lines in `config/settings.py` show as uncovered.

Browsable per-file report with highlighted uncovered lines: `docs/coverage/index.html` (open it in a browser).

## 3. Coverage by module

| Module | Statements | Covered | Line coverage |
|---|---|---|---|
| accounts | 240 | 219 | 91.2% |
| books | 162 | 87 | 53.7% |
| cart | 60 | 55 | 91.7% |
| config | 70 | 56 | 80.0% |
| (project root) | 18 | 0 | 0.0% |
| orders | 75 | 73 | 97.3% |

## 4. Coverage by file

| File | Statements | Missed | Line coverage | Missing lines |
|---|---|---|---|---|
| `accounts/apps.py` | 6 | 0 | 100% | - |
| `accounts/decorators.py` | 20 | 0 | 100% | - |
| `accounts/forms.py` | 47 | 3 | 94% | 51, 52, 53 |
| `accounts/models.py` | 40 | 12 | 70% | 13, 18, 29, 30, 31, 32, 34, 35, 36, 37, 39, 63 |
| `accounts/security_log.py` | 45 | 0 | 100% | - |
| `accounts/signals.py` | 9 | 0 | 100% | - |
| `accounts/throttling.py` | 33 | 4 | 88% | 37, 61, 63, 64 |
| `accounts/urls.py` | 4 | 0 | 100% | - |
| `accounts/views.py` | 36 | 2 | 94% | 17, 33 |
| `books/admin.py` | 8 | 0 | 100% | - |
| `books/apps.py` | 4 | 0 | 100% | - |
| `books/forms.py` | 17 | 2 | 88% | 20, 26 |
| `books/management/commands/seed_demo_data.py` | 43 | 43 | 0% | 1, 2, 4, 5, 7, 8, 10, 16, 22, 28, 33, 41, 44, 45, 47, 48, 52, 57, 58, 59, 61, 62, 63, 64, 67, 69, 70, 72, 73, 74, 75, 76, 78, 79, 85, 87, 88, 89, 93, 94, 96, 103, 105 |
| `books/management/commands/seed_performance_data.py` | 27 | 27 | 0% | 2, 3, 5, 6, 9, 10, 12, 13, 20, 21, 22, 24, 25, 26, 29, 31, 32, 37, 41, 43, 47, 49, 51, 52, 64, 66, 70 |
| `books/models.py` | 14 | 1 | 93% | 27 |
| `books/urls.py` | 4 | 0 | 100% | - |
| `books/views.py` | 45 | 2 | 96% | 122, 126 |
| `cart/admin.py` | 3 | 0 | 100% | - |
| `cart/apps.py` | 4 | 0 | 100% | - |
| `cart/models.py` | 14 | 1 | 93% | 37 |
| `cart/urls.py` | 4 | 0 | 100% | - |
| `cart/views.py` | 35 | 4 | 89% | 28, 29, 62, 63 |
| `config/asgi.py` | 4 | 4 | 0% | 1, 3, 6, 8 |
| `config/settings.py` | 59 | 6 | 90% | 14, 21, 32, 106, 112, 203 |
| `config/urls.py` | 3 | 0 | 100% | - |
| `config/wsgi.py` | 4 | 4 | 0% | 1, 3, 6, 8 |
| `locustfile.py` | 18 | 18 | 0% | 2, 4, 7, 8, 10, 11, 12, 18, 19, 20, 22, 28, 29, 30, 32, 38, 39, 40 |
| `orders/admin.py` | 4 | 0 | 100% | - |
| `orders/apps.py` | 4 | 0 | 100% | - |
| `orders/models.py` | 25 | 2 | 92% | 28, 56 |
| `orders/services.py` | 13 | 0 | 100% | - |
| `orders/urls.py` | 4 | 0 | 100% | - |
| `orders/views.py` | 25 | 0 | 100% | - |

## 5. Files below 90% and why

- `books/management/commands/seed_demo_data.py` (0%): Demo-data generator; run by hand, no automated test.
- `books/management/commands/seed_performance_data.py` (0%): NFR-01 load-test data generator; run by hand with Locust.
- `config/asgi.py` (0%): Server entry point; only executes when a real server starts.
- `config/wsgi.py` (0%): Server entry point; only executes when a real server starts.
- `locustfile.py` (0%): Load-test script for NFR-01; run with Locust, not part of the Django test suite.
- `accounts/models.py` (70%): `create_superuser`, its validation errors, missing-email/invalid-role errors and `__str__` have no direct test.
- `accounts/throttling.py` (88%): `client_ip` with no request, and the race where a counter expires between two cache calls (lines 61-64).
- `books/forms.py` (88%): Blank-after-trim title/author errors (lines 20, 26) have no test.
- `cart/views.py` (89%): GET (non-POST) requests to add-to-cart and remove-from-cart (lines 28-29, 62-63).
- `config/settings.py` (90%): Production-only branches (missing secret key, optional log file, TLS-proxy header). Their behaviour is tested in a child process the tool cannot see.

## 6. Reading the numbers honestly

- **78.4% line coverage is the measured result.** The five lowest-covered files are scripts and entry points that the test suite does not run (`seed_demo_data.py`, `seed_performance_data.py`, `locustfile.py`, `asgi.py`, `wsgi.py`). They hold 96 of the 625 statements.
- The core request-handling code (`orders`, `accounts/decorators.py`, `accounts/signals.py`, `accounts/security_log.py`, `orders/services.py`) is at or near 100%.
- Coverage shows which lines ran during tests. It does not show that the assertions are strong. A line can run without its result being checked.
- No test was added or changed to produce these numbers.

## 7. Suggested follow-ups (not done)

- Add tests for `create_superuser`/`create_user` validation, the blank title/author errors, and GET requests to the cart POST-only endpoints.
- Add a test that runs `seed_demo_data --sellers 2`.
