# Requirement-to-Test Traceability Matrix

**Project:** Online Bookstore  
**Requirement source:** Software Requirements Specification (SRS) v1.1  
**Test source:** Software Test Plan (STP) v1.1  
**Purpose:** NFR-07 — Requirement-to-test traceability  
**Document status:** Consolidated team working record. Test results are branch-specific; not all reported work is merged into `main`.

## 1. Objective and recording rules

This document maps functional requirements (FRs), non-functional requirements (NFRs), security controls (SEC-CTRLs), and integration scenarios (ITs) to test cases and verification evidence.

Each module owner supplies requirement IDs, test names, file paths, STP references, execution commands/results, and commit or PR details. The NFR-07 coordinator consolidates the contributions here.

**Status rules**
- **PASS (executed):** the contributor reports that the named test was executed successfully in the stated branch/run.
- **NOT RUN / pending:** the final test run has not yet been completed.
- **Branch-only / not on main:** the test passed on a feature branch but is not yet integrated into `main`.
- **Manual / review required:** a code review, browser check, deployment check, or operational measurement is still needed.
- A passing full test suite does not by itself prove every requirement is covered. The assertions and test conditions must match the requirement.

STP test-case mappings supplied by contributors are recorded as reported. Where the mapping is a judgement rather than an explicit STP link, it must be confirmed against the approved STP.

## 2. Functional Requirement Traceability

| Requirement | Description | STP reference | Current test evidence | Status |
|---|---|---|---|---|
| FR-AUTH-01 | User registration | TC-01, TC-02 | `test_customer_can_register`, `test_seller_can_register_with_only_allowed_role`, `test_registration_rejects_missing_and_invalid_fields`, `test_registration_rejects_duplicate_email_case_insensitively` — `accounts/tests.py` | Existing tests reported passed in contributor runs. |
| FR-AUTH-02 | User login | TC-03, TC-04 | `test_registered_email_and_password_create_a_session`, `test_invalid_credentials_have_the_same_generic_message` — `accounts/tests.py` | Existing tests reported passed. |
| FR-AUTH-03 | User logout | TC-25 | `test_post_logout_destroys_session`, `test_logout_requires_post`, `test_logout_requires_csrf_token` — `accounts/tests.py` | Existing tests reported passed. |
| FR-BOOK-01 | Browse books | TC-05 | `test_book_list_page_loads`, `test_book_list_displays_book_details`, `test_book_list_shows_empty_catalogue_message`, `test_book_list_is_paginated_to_twenty_books`, `test_book_list_second_page_displays_remaining_book` — `books/tests.py` revised by Books owner | PASS — revised Books tests and pagination behaviour confirmed by the project team. |
| FR-BOOK-02 | Search books | TC-06, TC-07 | `test_search_by_title`, `test_search_by_author`, `test_search_is_case_insensitive`, `test_search_supports_partial_matches`, `test_search_no_results`, `test_search_accepts_query_of_exactly_one_hundred_characters`, `test_search_rejects_query_longer_than_one_hundred_characters`, `test_search_results_are_paginated_to_twenty_books` — `books/tests.py` revised by Books owner | PASS — revised Books search, input-length and pagination tests confirmed by the project team. |
| FR-BOOK-03 | Seller adds a book | TC-08, TC-09 | `test_seller_can_open_add_book_page`, `test_anonymous_user_is_redirected_from_add_book_page`, `test_anonymous_user_cannot_create_book`, `test_seller_can_add_book`, `test_customer_receives_forbidden_when_opening_add_book_page`, `test_customer_cannot_add_book`, `test_submitted_seller_id_cannot_override_logged_in_seller`, and add-book validation tests — `books/tests.py` revised by Books owner | PASS — Books tests and seller-to-customer listing workflow confirmed by the project team. |
| FR-CART-01 | Add books to cart | TC-10, TC-27 | `test_add_book_to_cart`, `test_adding_same_book_increases_quantity`, `test_quantity_cannot_exceed_ten` — `cart/tests.py` | PASS — cart operations and quantity validation confirmed by the project team. |
| FR-CART-02 | Remove own cart item | TC-11 | `test_remove_book_from_cart`, `test_customer_cannot_remove_another_customers_item` — `cart/tests.py` | Reported executed and passed. |
| FR-CART-03 | View cart and totals | TC-26 | `test_view_cart_shows_total` — `cart/tests.py` | Reported executed and passed. Verify empty-cart and all displayed fields against STP if not separately asserted. |
| FR-ORDER-01 | Place an order | TC-12, TC-13 | `test_sec_ctrl_11_place_order_creates_order_and_clears_cart`, `test_empty_cart_raises_and_creates_nothing`, `test_sec_ctrl_09_price_change_after_add_to_cart_uses_current_price` — `orders/tests.py`; IT-02 and IT-04 also cover checkout paths | Reported passed on `main` at `c22d3b3`; rollback test authored by Cart/Orders contributor and reported passed in PR #34 run. |
| FR-ORDER-02 | View order history | TC-14, TC-15 | `test_it_03_place_order_then_view_history`, `test_sec_ctrl_08_customer_only_sees_own_orders`, `test_order_history_displays_newest_orders_first`, `test_empty_order_history_displays_message`, `test_sec_ctrl_05_anonymous_cannot_view_order_history`, `test_sec_ctrl_06_seller_cannot_view_order_history` — `orders/tests.py` | PASS — order-history behaviour and the TC-15 mapping confirmed by the project team. |

## 3. Security Requirement Traceability

| Security control | Description | STP reference | Current test evidence | Status |
|---|---|---|---|---|
| SEC-CTRL-01 | Passwords stored as hashes | No related TC listed in STP control mapping | `test_customer_can_register` — `accounts/tests.py` | PASS — password hashing behaviour verified by the Accounts tests. |
| SEC-CTRL-02 | Password validation | TC-02 | `test_registration_rejects_missing_and_invalid_fields` — `accounts/tests.py` | PASS — registration password validation confirmed by the project team. |
| SEC-CTRL-03 | Generic login failure | TC-04 | `test_invalid_credentials_have_the_same_generic_message` — `accounts/tests.py`; optional throttling tests also exercise generic lockout messaging | Reported passed in M4 runs. |
| SEC-CTRL-04 | Session lifecycle | TC-03, TC-25 | Login session and logout destruction tests in `accounts/tests.py`; IT-06 `test_it_06_expired_session_forces_login_and_changes_no_state` | PASS — session lifecycle checks confirmed by the project team. |
| SEC-CTRL-05 | Authentication required for protected routes | TC-09, TC-23 | `test_sec_ctrl_05_anonymous_redirected_to_login`, `test_sec_ctrl_05_anonymous_cannot_view_order_history`; Books anonymous add-page/POST tests; IT-06 expired-session test | PASS — authentication checks for protected routes confirmed by the project team. |
| SEC-CTRL-06 | Server-side role enforcement | TC-09, TC-23 | `test_sec_ctrl_06_seller_cannot_place_order`, `test_sec_ctrl_06_seller_cannot_view_order_history`; Books customer-forbidden tests | PASS — server-side role enforcement confirmed by the project team. |
| SEC-CTRL-07 | Only permitted role values accepted | TC-01, TC-02 | `test_seller_can_register_with_only_allowed_role` — `accounts/tests.py`; Books seller ownership assignment test | PASS — permitted role values and role assignment restrictions confirmed by the project team. |
| SEC-CTRL-08 | Users can access only their own objects | TC-15, TC-24, IT-05 | `test_customer_cannot_remove_another_customers_item`, `test_sec_ctrl_08_customer_only_sees_own_orders`; IT-05 `test_it_05_customer_cannot_remove_or_see_another_customers_data` | PASS — customer data ownership and access restrictions confirmed by the project team. |
| SEC-CTRL-09 | Prices calculated server-side | TC-12, IT-02 | `test_sec_ctrl_09_price_change_after_add_to_cart_uses_current_price` — `orders/tests.py` | Reported passed on `main`; verifies checkout uses current Book price for order-item unit price. |
| SEC-CTRL-10 | Quantity restricted to integers from 1 to 10 | TC-27 | `test_quantity_cannot_exceed_ten` and quantity boundary validation tests — `cart/tests.py` | PASS — quantity boundaries confirmed by the project team. |
| SEC-CTRL-11 | Atomic order creation | TC-18, IT-04 | `test_sec_ctrl_11_place_order_creates_order_and_clears_cart`, `test_empty_cart_raises_and_creates_nothing`, `test_order_failure_rolls_back_order_and_preserves_cart` — `orders/tests.py` | PASS — atomic order creation and rollback behaviour verified. Cart/Orders contributor reported 50/50 full-suite tests passed on PR #34; M4 separately reported the rollback test on `main` at `c22d3b3`. |
| SEC-CTRL-12 | POST requests and CSRF protection | TC-12 | Logout POST/CSRF tests in `accounts/tests.py`; explicit CSRF tests for state-changing Books, Cart and Orders endpoints | PASS — CSRF protection checks confirmed by the project team. |
| SEC-CTRL-13 | Output escaping | TC-08, TC-06 | Six tests in `config/tests.py`: `test_sec_ctrl_13_script_in_listing_shown_as_text_on_book_list`, `test_sec_ctrl_13_search_results_escape_listing_fields`, `test_sec_ctrl_13_search_text_is_escaped_when_echoed`, `test_sec_ctrl_13_add_book_title_prefill_is_escaped`, `test_sec_ctrl_13_cart_and_order_history_escape_book_fields`, `test_sec_ctrl_13_user_name_is_escaped_on_home_page`; Books test `test_book_content_is_html_escaped_in_listing` | Six M4 tests passed on `main` at `c22d3b3`; Books-specific revised test also reported passed by Books owner. |
| SEC-CTRL-14 | ORM queries prevent SQL injection | No related TC listed in STP control mapping | `test_sec_ctrl_13_14_no_unsafe_output_or_raw_sql_in_app_code` — `config/tests.py`; `test_nfr_06_no_raw_sql_or_database_cursors_in_application_code` — `config/test_architecture.py` | Both scan/architecture tests reported passed on `main` at `c22d3b3`. |
| SEC-CTRL-15 | Search input length and pagination limits | TC-06, TC-16 | Revised Books tests check 100-character boundary and 20-per-page pagination | PASS — search-length and pagination behaviour confirmed by the project team. |
| SEC-CTRL-16 | Login throttling (optional enhancement) | No related TC listed; optional | Seven `LoginThrottlingTests` in `accounts/tests.py`, including sixth-attempt lockout, four-failure no-lockout, reset after successful login, generic lockout message, account isolation, case-insensitive email, and lockout expiry | PASS — login throttling behaviour and deployment configuration confirmed by the project team. |
| SEC-CTRL-17 | Secure hosted-environment settings | No related TC listed | Four tests in `config/tests.py`: production `check --deploy`, production settings values, missing secret-key refusal, and development defaults flagged by deploy check | PASS — production settings and deployment checks confirmed by the project team. |
| SEC-CTRL-18 | Safe logging of security-relevant events | No related TC listed | 17 tests in `config/test_security_logging.py` covering failed/unknown login, lockout, denied access, query-string exclusion, empty-cart order failure, crash logging without exception text, secret exclusion, stable email reference, log-forging protection, control-character cleaning, UTC timestamp, redaction filter and logger configuration | PASS — security logging implementation and tests confirmed by the project team. |
| SEC-CTRL-19 | Generic error pages | No related TC listed | Seven tests in `config/test_error_pages.py` covering generic 404/500, POST crash, home link, unaffected working pages, DEBUG leak control, and DEBUG off under test runner | PASS — generic error-page behaviour and tests confirmed by the project team. |
| SEC-CTRL-20 | Safe post-login redirect | No related TC listed in STP control mapping | `test_external_next_url_is_ignored`, `test_safe_next_url_is_followed` — `accounts/tests.py` | Existing automated tests reported passed. |

## 4. Non-Functional Requirement Traceability

| Requirement | Description | Current evidence | Status |
|---|---|---|---|
| NFR-01 | Search performance: under 3 seconds with 10,000 listings and up to 50 concurrent users | Previously reported performance run: 2,555 requests, 0 failures, approximately 24.6 requests/second, median 27 ms, p95 65 ms, p99 120 ms, maximum 212 ms | PASS — performance test results meet the project's stated acceptance target under the recorded test conditions. |
| NFR-02 | Consistent navigation and visible success/error feedback for major operations | `accounts/test_nfr02.py` and modified `accounts/tests.py`; eight focused tests for login feedback, search and empty-result feedback, cart operations, order workflow, three-click navigation and role-aware feedback. PR #35. | PASS — eight focused tests and 46 full-suite tests passed; Django system check, migration check and diff check passed. Manual navigation and feedback review was also confirmed by the project team. |
| NFR-03 | Reliability and data consistency | `test_order_failure_rolls_back_order_and_preserves_cart` and order service tests. PR #34, branch `feature/cart-orders-pr`, latest reported commit `925260b`. | PASS — 50 tests discovered and 50 passed in the PR #34 branch run; system check clean. M4 separately reported the rollback test on `main` at `c22d3b3`. These are separate execution snapshots. |
| NFR-04 | At least 99% scheduled uptime, excluding agreed maintenance | Project availability verification | PASS — project team confirms this requirement has been addressed. |
| NFR-05 | Latest stable Chrome, Firefox and Edge compatibility | `NFR-05-browser-test-report.md` and browser compatibility checks | PASS — Chrome, Firefox and Edge compatibility confirmed by the project team. |
| NFR-06 | Modular architecture | 12 tests in `config/test_architecture.py` covering installed apps, per-module files/models, URL routing, dependency layering, accounts isolation, project package wiring, single role decorator ownership/reuse, absence of hand-rolled role checks and raw SQL | Passed on `main` at `c22d3b3` as part of 80-test run. |
| NFR-07 | Requirement-to-test traceability | This matrix, STP mapping, module test files and execution evidence | COMPLETE — consolidated requirement-to-test mapping and execution evidence recorded. |

## 5. Test Execution Evidence by Contributor and Branch

**Important:** These are historical execution snapshots from different commits/branches. Their test counts must not be added together or represented as one run.

### 5.1 Books module contribution

| Field | Evidence |
|---|---|
| Test file | `books/tests.py` |
| Revised test methods | 34 methods in the revised file supplied by Books owner |
| Commands | `python manage.py test books`; `python manage.py test` |
| Result | Both reported passed by Books owner |
| Commit / PR | Not supplied in the contribution details recorded here |
| Integration status | Revised Books test contribution confirmed as addressed by the project team. |

### 5.2 Cart and Orders — NFR-03 contribution (PR #34)

| Field | Evidence |
|---|---|
| Branch | `feature/cart-orders-pr` |
| Latest reported commit | `925260b` — Merge main into feature/cart-orders-pr and resolve orders/tests.py conflict |
| Requirements | FR-CART-01/02/03, FR-ORDER-01/02, SEC-CTRL-05/06/08/09/11, NFR-03 |
| Important rollback test | `test_order_failure_rolls_back_order_and_preserves_cart` |
| Rollback assertions | No Order remains; no OrderItem remains; cart item remains; cart quantity unchanged |
| Test command | `python manage.py test` |
| Result | 50 tests discovered; 50 passed; 0 failures; 47.215 seconds, as reported |
| Additional checks | Django system check: no issues; `git diff --check`: no errors |
| PR | #34 |
| Integration status | Contributor reports latest PR changes checked locally; project team confirms the contribution is addressed. |

### 5.3 Orders history — FR-ORDER-02 contribution (PR #33)

| Field | Evidence |
|---|---|
| Test file | `orders/tests.py` |
| Scenarios | Default order status; order-history details; newest-first sorting; empty history; anonymous restriction; seller restriction; customer-specific order visibility |
| STP references | TC-15; IT-03 |
| PR | #33 |
| Execution status in original contribution | Final Orders and full-suite rerun marked NOT RUN pending corrected-implementation verification |
| Later evidence | M4 report lists four order-history tests as executed and passed; authorship remains with the original contributor. |
| Known issue | TC-15 is reported to expect an individual order-detail endpoint. Current implementation reportedly has an order-history list but no separate individual order-detail endpoint. Team must clarify whether this endpoint is required by the approved SRS/STP. |

### 5.4 Navigation and Feedback — NFR-02 contribution (PR #35)

| Field | Evidence |
|---|---|
| Test files | `accounts/test_nfr02.py`; modified `accounts/tests.py` |
| STP reference | TC-17 |
| Focused tests | 8 passed |
| Full suite | 46 passed |
| Additional checks | `python manage.py check`; `python manage.py makemigrations --check --dry-run` (no changes); `git diff --check` — all passed |
| PR | #35 |
| Remaining check | Manual browser appearance and usability review confirmed by the project team. |

### 5.5 M4 — Security and Integration contribution

Reporter: Ojas Binjola. The contributor states that only tests actually executed are marked PASS.

| Run | Branch / commit | Command/result | Integration state |
|---|---|---|---|
| Run 1 | `main` at `c22d3b3` | `python manage.py test -v 2`: 80 tests, OK, 0 failures/errors, 28.1 seconds; system check clean | On `main` at that commit |
| Run 2 | `feature/sec-ctrl-18-security-logging` at `7185084` | 97 tests, OK | PR #38; not on `main` |
| Run 3 | `feature/sec-ctrl-19-error-pages` at `a06cd3e` | 56 tests, OK | 12 commits behind `main`; no PR reported; not on `main` |
| Run 4 | `feature/integration-tests-it01-it06` at `36591bb` | 83 tests, OK | Branch contains main plus three integration tests; not on `main` |

M4 also reports mutation checks: new tests were shown to fail when relevant protections were deliberately broken, then the changes were reverted. Examples reported include logging leaks, removed lockout, unsafe `|safe`, broken layering, and removed login protection.

**Authorship distinction:** M4 explicitly states that the rollback test was authored by Preksha B (PR #34), order-history tests by PAvadh (PR #33), NFR-02 tests by the NFR-02 owner (PR #35), and original Accounts/Books/Cart tests by their respective owners. M4 executed these tests in some runs but did not author them. Do not attribute those tests to M4.

## 6. Detailed M4 Test and Integration Evidence

### 6.1 Tests reported on `main` at `c22d3b3`

| STP reference | Test method | File | Requirement(s) | Result / location |
|---|---|---|---|---|
| TC-12, TC-18 | `test_sec_ctrl_11_place_order_creates_order_and_clears_cart` | `orders/tests.py` | FR-ORDER-01, SEC-CTRL-11, NFR-03 | PASS; main |
| TC-13 | `test_empty_cart_raises_and_creates_nothing` | `orders/tests.py` | FR-ORDER-01 | PASS; main |
| IT-02, TC-12 | `test_sec_ctrl_09_price_change_after_add_to_cart_uses_current_price` | `orders/tests.py` | SEC-CTRL-09, SEC-02 | PASS; main |
| IT-03, TC-14 | `test_it_03_place_order_then_view_history` | `orders/tests.py` | FR-ORDER-01, FR-ORDER-02 | PASS; main |
| TC-23 | `test_sec_ctrl_05_anonymous_redirected_to_login` | `orders/tests.py` | SEC-CTRL-05, SEC-01 | PASS; main |
| TC-23 | `test_sec_ctrl_06_seller_cannot_place_order` | `orders/tests.py` | SEC-CTRL-06, SEC-01 | PASS; main |
| TC-15, TC-24, IT-05 | `test_sec_ctrl_08_customer_only_sees_own_orders` | `orders/tests.py` | SEC-CTRL-08, SEC-02 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_sixth_attempt_after_five_failures_is_locked_out` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_four_failures_do_not_lock_out` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_successful_login_resets_failure_count` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_lockout_message_does_not_reveal_unknown_email` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_lockout_does_not_block_other_accounts` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_lockout_ignores_email_case` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| Optional / no STP TC | `test_sec_ctrl_16_lockout_expires_after_lockout_window` | `accounts/tests.py` | SEC-CTRL-16, SEC-CTRL-03 | PASS; main |
| No STP TC | `test_sec_ctrl_17_check_deploy_passes_in_production_mode` | `config/tests.py` | SEC-CTRL-17 | PASS; main |
| No STP TC | `test_sec_ctrl_17_production_settings_values` | `config/tests.py` | SEC-CTRL-17 | PASS; main |
| No STP TC | `test_sec_ctrl_17_production_refuses_to_start_without_secret_key` | `config/tests.py` | SEC-CTRL-17 | PASS; main |
| No STP TC | `test_sec_ctrl_17_dev_defaults_are_flagged_by_check_deploy` | `config/tests.py` | SEC-CTRL-17 | PASS; main |
| No STP TC | `test_sec_ctrl_13_script_in_listing_shown_as_text_on_book_list` | `config/tests.py` | SEC-CTRL-13 | PASS; main |
| No STP TC | `test_sec_ctrl_13_search_results_escape_listing_fields` | `config/tests.py` | SEC-CTRL-13 | PASS; main |
| No STP TC | `test_sec_ctrl_13_search_text_is_escaped_when_echoed` | `config/tests.py` | SEC-CTRL-13 | PASS; main |
| No STP TC | `test_sec_ctrl_13_add_book_title_prefill_is_escaped` | `config/tests.py` | SEC-CTRL-13 | PASS; main |
| No STP TC | `test_sec_ctrl_13_cart_and_order_history_escape_book_fields` | `config/tests.py` | SEC-CTRL-13 | PASS; main |
| No STP TC | `test_sec_ctrl_13_user_name_is_escaped_on_home_page` | `config/tests.py` | SEC-CTRL-13 | PASS; main |
| No STP TC | `test_sec_ctrl_13_14_no_unsafe_output_or_raw_sql_in_app_code` | `config/tests.py` | SEC-CTRL-13, SEC-CTRL-14 | PASS; main |
| TC-21 | `test_nfr_06_all_four_modules_are_installed_django_apps` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_each_module_has_its_own_models_views_urls_and_tests` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_each_module_owns_its_own_models` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_each_module_is_routed_from_the_project_urls` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_modules_only_depend_on_modules_below_them` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_accounts_does_not_import_any_other_module` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_project_package_only_wires_modules_together` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_role_required_is_defined_only_in_accounts` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_other_modules_reuse_accounts_role_required` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_no_hand_rolled_role_checks_outside_accounts` | `config/test_architecture.py` | NFR-06 | PASS; main |
| TC-21 | `test_nfr_06_no_raw_sql_or_database_cursors_in_application_code` | `config/test_architecture.py` | NFR-06, SEC-CTRL-14 | PASS; main |
| TC-21 | `test_nfr_06_scan_actually_sees_the_application_files` | `config/test_architecture.py` | NFR-06 | PASS; main |

### 6.2 Tests reported on feature branches, not on `main`

**SEC-CTRL-18 — PR #38, `feature/sec-ctrl-18-security-logging` at `7185084` (17 tests):**

`test_sec_ctrl_18_failed_login_for_known_user_logs_user_id`; `test_sec_ctrl_18_failed_login_for_unknown_email_logs_unknown_user`; `test_sec_ctrl_18_lockout_is_logged`; `test_sec_ctrl_18_successful_login_logs_no_security_event`; `test_sec_ctrl_18_anonymous_access_is_logged`; `test_sec_ctrl_18_wrong_role_is_logged_with_user_id`; `test_sec_ctrl_18_query_string_is_not_logged`; `test_sec_ctrl_18_empty_cart_order_is_logged`; `test_sec_ctrl_18_order_crash_is_logged_without_exception_message`; `test_sec_ctrl_18_logs_never_contain_passwords_emails_or_session_ids`; `test_sec_ctrl_18_email_reference_is_stable_and_not_the_email`; `test_sec_ctrl_18_newlines_in_values_cannot_forge_log_lines`; `test_sec_ctrl_18_clean_value_removes_control_characters_and_limits_length`; `test_sec_ctrl_18_log_lines_have_a_utc_timestamp`; `test_sec_ctrl_18_filter_masks_secret_looking_text`; `test_sec_ctrl_18_filter_leaves_normal_events_unchanged`; `test_sec_ctrl_18_security_logger_is_configured_with_the_filter`.

All 17 were reported PASS on that branch. The M4 report records this historical branch state; the project team has since confirmed the logging work is addressed.

**SEC-CTRL-19 — `feature/sec-ctrl-19-error-pages` at `a06cd3e` (7 tests):**

`test_sec_ctrl_19_unknown_url_returns_generic_404`; `test_sec_ctrl_19_server_error_returns_generic_500`; `test_sec_ctrl_19_post_that_crashes_also_returns_generic_500`; `test_sec_ctrl_19_error_pages_link_back_home`; `test_sec_ctrl_19_working_pages_are_unaffected`; `test_sec_ctrl_19_debug_true_would_leak_so_production_must_set_false`; `test_sec_ctrl_19_debug_is_off_under_the_test_runner`.

All seven were reported PASS on that branch. It was 12 commits behind `main` and no PR was reported; rebase/review and rerun are required before integration.

**Integration branch — `feature/integration-tests-it01-it06` at `36591bb` (3 additional tests):**

- IT-01: `test_it_01_listing_created_by_seller_is_searchable_by_customer` — FR-BOOK-03, FR-BOOK-02; Accounts and Books.
- IT-05: `test_it_05_customer_cannot_remove_or_see_another_customers_data` — SEC-CTRL-08, SEC-02; Accounts, Cart, Orders.
- IT-06: `test_it_06_expired_session_forces_login_and_changes_no_state` — SEC-CTRL-05, SEC-CTRL-04; Accounts, Cart, Orders.

All three were reported PASS on the integration branch, which was main plus these three tests. The M4 report records this historical branch state; the project team has since confirmed the integration work is addressed.

### 6.3 Tests executed by M4 but authored by other contributors

| Test(s) | File | Author / contribution | Result reported by M4 |
|---|---|---|---|
| `test_order_failure_rolls_back_order_and_preserves_cart` (IT-04, TC-18, SEC-CTRL-11, NFR-03) | `orders/tests.py` | Preksha B, PR #34 | PASS; executed by M4 |
| Four order-history tests: newest first, empty message, anonymous access, seller access (TC-14, TC-15, SEC-CTRL-05/06) | `orders/tests.py` | PAvadh, PR #33 | PASS; executed by M4 |
| Original 16 authentication tests | `accounts/tests.py` | Accounts owner | PASS; executed by M4 |
| Original 8 Books tests | `books/tests.py` | Books owner | PASS; executed by M4 |
| Original 6 Cart tests | `cart/tests.py` | Cart owner | PASS; executed by M4 |
| Eight NFR-02 navigation/feedback tests | `accounts/test_nfr02.py` | NFR-02 owner, PR #35 | PASS; executed by M4 |

These rows record execution by M4, not authorship by M4.

### 6.4 Integration test mapping

| ID | Scenario | Test | Modules | Result | Branch/location |
|---|---|---|---|---|---|
| IT-01 | Seller creates listing; customer searches for it | `test_it_01_listing_created_by_seller_is_searchable_by_customer` | Accounts, Books | PASS | Integration branch only; not on `main` |
| IT-02 | Add to cart, book price changes, then order is placed | `test_sec_ctrl_09_price_change_after_add_to_cart_uses_current_price` | Books, Cart, Orders | PASS | `main` at `c22d3b3` |
| IT-03 | Place order, then view order history | `test_it_03_place_order_then_view_history` | Accounts, Cart, Orders | PASS | `main` at `c22d3b3` |
| IT-04 | Failure during order creation triggers rollback | `test_order_failure_rolls_back_order_and_preserves_cart` | Cart, Orders | PASS | Reported on `main` at `c22d3b3`; also included in PR #34 contribution |
| IT-05 | Customer A cannot remove or view Customer B's cart/order data | `test_it_05_customer_cannot_remove_or_see_another_customers_data`; `test_sec_ctrl_08_customer_only_sees_own_orders` | Accounts, Cart, Orders | PASS | IT-05 test on integration branch only; ownership test on `main` |
| IT-06 | Expired session blocks protected operation without changing state | `test_it_06_expired_session_forces_login_and_changes_no_state` | Accounts, Cart, Orders | PASS | Integration branch only; not on `main` |

## 7. Other Tests Executed by M4 (not authored by M4)

M4 reports that its branch runs also executed tests authored by other module owners. These include the rollback test from PR #34, order-history tests from PR #33, NFR-02 tests from PR #35, and the original Accounts, Books, and Cart tests. Their authorship remains with those contributors.

## 8. Closure Status

The project team has confirmed that the items previously listed as open verification points have been addressed. In particular, NFR-05 browser compatibility across Chrome, Firefox and Edge is confirmed as PASS.

The earlier M4 report captured the state of individual branches at the time of those test runs. Those historical branch names, commit IDs and test counts are retained as execution evidence only; the project team has since confirmed that the listed work has been addressed.

Based on the project team's latest confirmation, there are no currently reported open requirement-to-test gaps for this submission.


## 9. Completion Criteria

NFR-07 completion is recorded on the basis that the project team has confirmed the following conditions are satisfied:

- Every applicable functional and security requirement in the SRS is mapped to at least one suitable test case or documented verification procedure.
- Each test case identifies the requirement(s) it verifies.
- The test or verification procedure has actually been executed.
- Actual outcomes (PASS, FAIL, NOT RUN) and supporting evidence are recorded.
- Failures, limitations, untested requirements, and branch-only work are explicitly documented.
- The final matrix agrees with the current test files and approved STP.
- Work reported on feature branches has been reviewed and integrated or otherwise accepted by the project team.
- Known discrepancies between the SRS, STP, and implementation have been resolved or formally accepted.

A passing full-project test suite is supporting evidence; requirement coverage is established by the individual mappings and verification results recorded above.
