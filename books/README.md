# Books Module

## 1. Overview

The `books` module implements book browsing, searching, and seller listing creation for the Online Bookstore application.

**Owner:** Rahul M S

## 2. Functional Requirements

| ID         | Requirement      | Description                                                                 |
| ---------- | ---------------- | --------------------------------------------------------------------------- |
| FR-BOOK-01 | Browse Books     | Allow anonymous visitors, customers, and sellers to browse available books. |
| FR-BOOK-02 | Search Books     | Support case-insensitive partial searches by book title or author.          |
| FR-BOOK-03 | Add Book Listing | Allow authenticated sellers to create book listings.                        |

## 3. File Responsibilities

| File or Directory                              | Responsibility                                                |
| ---------------------------------------------- | ------------------------------------------------------------- |
| `apps.py`                                      | Django application configuration                              |
| `models.py`                                    | Book model and seller relationship                            |
| `forms.py`                                     | Validation for book listing creation                          |
| `views.py`                                     | Browse, search, and add-book request handling                 |
| `urls.py`                                      | URL routes for book functionality                             |
| `admin.py`                                     | Register the Book model in Django admin                       |
| `tests.py`                                     | Tests for browsing, searching, validation, and access control |
| `migrations/`                                  | Database migration files                                      |
| `templates/books/book_list.html`               | Book browsing page                                            |
| `templates/books/book_search.html`             | Search results page                                           |
| `templates/books/book_form.html`               | Seller listing creation page                                  |
| `management/commands/seed_performance_data.py` | Generate synthetic books for performance testing              |
| `locustfile.py` (project root)                 | Simulate concurrent book-search requests during load testing  |

## 4. Implemented Features

### 4.1 Browse Books

- Displays available book listings on the browsing page.
- Supports pagination where configured.
- Allows users to navigate to the book listing page from the homepage.
- Uses Django's ORM to retrieve book records.

### 4.2 Search Books

- Searches book titles and authors using case-insensitive partial matching.
- Displays matching book listings.
- Handles searches with no matching results.
- Supports pagination where configured.
- Limits the search query length to 100 characters.
- Allows users to access search from the homepage and book pages.

### 4.3 Seller Book Listings

- Allows authenticated sellers to access the add-book form.
- Provides a seller-only option to add a listing from the homepage.
- Provides sellers with a direct option to start creating a listing from the search page.
- Supports pre-filling the book title from a search query.
- Associates a newly created listing with the authenticated seller on the server side.
- Saves book listings through Django's ORM.
- Restricts listing creation to sellers through server-side role checks.

Customers can browse and search books but must not be allowed to create listings, including by accessing the add-book URL directly.

### 4.4 Homepage Navigation

The homepage provides navigation to the main bookstore features.

- **Browse Books:** Opens the book listing page.
- **Search Books:** Searches for books by title or author.
- **Add a Book Listing:** Available to authenticated sellers only.
- **My Orders:** Provides access to order history.
- **Log In / Register:** Provides account access to unauthenticated visitors.

## 5. Book Routes

| Route                      | Purpose                   | Access                     |
| -------------------------- | ------------------------- | -------------------------- |
| `/books/`                  | Browse available books    | Public                     |
| `/books/search/?q=<query>` | Search by title or author | Public                     |
| `/books/add/`              | Create a book listing     | Authenticated sellers only |

The add-book form accepts a `title` query parameter to prefill the title field when a seller starts a listing from a search query.

## 6. Non-Functional Requirement: NFR-01

### Objective

Ensure book search results are displayed within three seconds under normal operating conditions.

### Acceptance Criteria

- Search results display within three seconds under normal operating conditions.
- The test environment supports a catalogue of up to 10,000 listings.
- The test environment supports up to 50 concurrent users.
- Test results and performance issues are documented.

### Test Environment

| Parameter             | Configuration                   |
| --------------------- | ------------------------------- |
| Application framework | Django                          |
| Database              | SQLite                          |
| Server                | Local Django development server |
| Load-testing tool     | Locust                          |
| Synthetic catalogue   | 10,000 book listings            |
| Concurrent users      | 50                              |

### Observed Load-Test Results

The following results were recorded in the Locust statistics after a test with 50 concurrent users.

| Metric                         |      Observed Result |
| ------------------------------ | -------------------: |
| Total requests                 |                2,939 |
| Failed requests                |                    0 |
| Throughput                     | 23.3 requests/second |
| Median response time           |                26 ms |
| 95th-percentile response time  |                67 ms |
| 99th-percentile response time  |               120 ms |
| Maximum observed response time |               478 ms |

#### Results by Search Type

| Search Type            | 95th-Percentile Response Time | Maximum Response Time |
| ---------------------- | ----------------------------: | --------------------: |
| Author search          |                         71 ms |                412 ms |
| Common title search    |                         75 ms |                478 ms |
| Search with no results |                         51 ms |                 86 ms |
| Specific title search  |                         58 ms |                435 ms |

### Performance Assessment

All observed search response times were below the three-second target during the recorded test. No failed requests were reported.

The measured results provide preliminary evidence that the search implementation meets the response-time target in the tested local environment.

These measurements are specific to the local SQLite and Django development-server configuration. They do not establish production performance or guarantee the same results on different hardware or deployment configurations.

No search-query optimization has been justified by these measurements so far.

### Performance Test Files

- `books/management/commands/seed_performance_data.py` — generates synthetic book listings for testing.
- `locustfile.py` — defines the book-search load-test scenarios.

The synthetic dataset is intended for performance testing and should not be treated as production catalogue data.

## 7. Integration Dependencies

### Accounts Module — Pooja

- Use the shared Django User model.
- Use the agreed role field and role values.
- Use the agreed `role_required` decorator for seller-only access.
- Do not implement a separate user or role system inside `books`.

### Cart and Orders Modules

- Cart references the Book model using a foreign key.
- Cart must not maintain a separate copy of the current book price.
- Orders reads the current book price at purchase time and stores it as the order item's unit price, according to the agreed integration contract.

### Shared UI

The templates currently provide basic functional HTML and navigation. They are not the final shared UI design.

When the team establishes the shared base template, navigation, and message-display conventions, these templates should be updated to follow them.

## 8. Scope Boundaries

This module covers:

- Book browsing
- Book searching
- Seller book listing creation
- Book-related access control
- Book-search performance testing

It does not implement cart operations, order processing, payment processing, or other functionality assigned to separate modules.

## 9. Development and Testing Commands

Run the following commands from the directory containing `manage.py`.

Check the Django configuration:

```bash
python manage.py check
```

Run the Books module tests:

```bash
python manage.py test books
```

Generate the default performance dataset:

```bash
python manage.py seed_performance_data
```

Start the Django development server:

```bash
python manage.py runserver
```

Run the Locust load test:

```bash
python -m locust -f locustfile.py --host http://127.0.0.1:8000
```

The performance-data command should only be used in an appropriate development or test environment. Review its cleanup behavior before rerunning it, and never use synthetic-data cleanup against production records.
