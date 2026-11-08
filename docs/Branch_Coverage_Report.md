# Branch Coverage Report

**Project:** Online Bookstore (Django)  
**Reporter:** Ojas Binjola (M4, Security & Integration)  
**Measured on:** `main` at commit `6b7ad27` (after PRs #42 and #43), 2026-11-08  
**Tool:** Coverage.py 7.16.2, Django 5.2  
**Test run:** `python manage.py test` — 133 tests, all passed (OK)  

## 1. Result

| Measure | Covered | Total | Percentage |
|---|---|---|---|
| **Branch coverage** | 62 | 100 | **62.0%** |
| Partially covered branch points | 20 | - | - |

A branch is one outcome of a decision (for example the `if` taken, or not taken). A line can run while one of its two outcomes never does; that is a *partial* branch.

## 2. How it was measured

Same run as the line-coverage report, with branch tracking (`--branch`) switched on:

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

Browsable summary: `docs/branch-coverage/index.html`. The full line-by-line view with branch markers is `docs/coverage/index.html`.

## 3. Branch coverage by module

| Module | Branches | Covered | Missed | Branch coverage |
|---|---|---|---|---|
| accounts | 46 | 34 | 12 | 73.9% |
| books | 32 | 14 | 18 | 43.8% |
| cart | 8 | 6 | 2 | 75.0% |
| config | 12 | 6 | 6 | 50.0% |
| orders | 2 | 2 | 0 | 100.0% |

## 4. Branch coverage by file (files with branches)

| File | Branches | Covered | Missed | Partial | Branch coverage |
|---|---|---|---|---|---|
| `accounts/decorators.py` | 4 | 4 | 0 | 0 | 100.0% |
| `accounts/forms.py` | 10 | 8 | 2 | 2 | 80.0% |
| `accounts/models.py` | 10 | 4 | 6 | 2 | 40.0% |
| `accounts/security_log.py` | 10 | 9 | 1 | 1 | 90.0% |
| `accounts/throttling.py` | 6 | 5 | 1 | 1 | 83.3% |
| `accounts/views.py` | 6 | 4 | 2 | 2 | 66.7% |
| `books/forms.py` | 4 | 2 | 2 | 2 | 50.0% |
| `books/management/commands/seed_demo_data.py` | 8 | 0 | 8 | 0 | 0.0% |
| `books/management/commands/seed_performance_data.py` | 6 | 0 | 6 | 0 | 0.0% |
| `books/views.py` | 14 | 12 | 2 | 2 | 85.7% |
| `cart/views.py` | 8 | 6 | 2 | 2 | 75.0% |
| `config/settings.py` | 12 | 6 | 6 | 6 | 50.0% |
| `orders/services.py` | 2 | 2 | 0 | 0 | 100.0% |

## 5. Branches never taken

**`accounts/forms.py`**

- line 50 `if data is not None and "email" not in data and "username" in data:` never went to line 51
- line 63 `if email and password:` never went to line 93

**`accounts/models.py`**

- line 12 `if not email:` never went to line 13
- line 17 `if role not in UserRole.values:` never went to line 18
- line 34 `if extra_fields.get("is_staff") is not True:` never went to line 35
- line 34 `if extra_fields.get("is_staff") is not True:` never went to line 36
- line 36 `if extra_fields.get("is_superuser") is not True:` never went to line 37
- line 36 `if extra_fields.get("is_superuser") is not True:` never went to line 39

**`accounts/security_log.py`**

- line 93 `if secret:` never went to line 95

**`accounts/throttling.py`**

- line 36 `if request is None:` never went to line 37

**`accounts/views.py`**

- line 16 `if request.user.is_authenticated:` never went to line 17
- line 19 `if request.method == "POST":` never went to line 33

**`books/forms.py`**

- line 19 `if not title:` never went to line 20
- line 25 `if not author:` never went to line 26

**`books/management/commands/seed_demo_data.py`**

- line 61 `if options["clear"]:` never went to line 62
- line 61 `if options["clear"]:` never went to line 69
- line 73 `for i in range(1, n_sellers + 1):` never went to line 74
- line 73 `for i in range(1, n_sellers + 1):` never went to line 105
- line 75 `if User.objects.filter(email=email).exists():` never went to line 76
- line 75 `if User.objects.filter(email=email).exists():` never went to line 78
- line 87 `for _ in range(rng.randint(2, 3)):` never went to line 73
- line 87 `for _ in range(rng.randint(2, 3)):` never went to line 88

**`books/management/commands/seed_performance_data.py`**

- line 24 `if count < 1:` never went to line 25
- line 24 `if count < 1:` never went to line 29
- line 31 `if seller is None:` never went to line 32
- line 31 `if seller is None:` never went to line 41
- line 51 `for i in range(count):` never went to line 52
- line 51 `for i in range(count):` never went to line 64

**`books/views.py`**

- line 57 `if query:` never went to line 63
- line 121 `if len(title) > MAX_SEARCH_LENGTH:` never went to line 122

**`cart/views.py`**

- line 27 `if request.method != "POST":` never went to line 28
- line 61 `if request.method != "POST":` never went to line 62

**`config/settings.py`**

- line 12 `if value is None:` never went to line 14
- line 19 `if value is None:` never went to line 21
- line 30 `if not SECRET_KEY:` never went to line 38
- line 31 `if not DEBUG:` never went to line 32
- line 105 `if os.environ.get("DJANGO_SECURITY_LOG_FILE"):` never went to line 106
- line 202 `if env_bool("DJANGO_BEHIND_TLS_PROXY", False):` never went to line 203

## 6. Reading the numbers honestly

- **62.0% branch coverage is the measured result** (62 of 100 branches). It is lower than line coverage (78.4%) because several error and edge-case outcomes are never exercised.
- 14 of the 38 missed branches are in the two demo-data scripts, which no automated test runs.
- `config/settings.py` shows missed branches that belong to production-only code. They are tested through a child process (`manage.py check --deploy` with production variables) that Coverage.py cannot measure.
- The `orders` module has 100.0% branch coverage (2 of 2).
- No test was added or changed to produce these numbers.
