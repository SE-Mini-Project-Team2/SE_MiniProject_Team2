# Books Module

## Overview

The `books` module implements the book-related functionality of the Online Bookstore application.

**Owner:** Rahul M S

## Functional Requirements

- **FR-BOOK-01 — Browse Books:** Allow anonymous visitors, customers, and sellers to browse available books.
- **FR-BOOK-02 — Search Books:** Support case-insensitive partial searches by book title or author.
- **FR-BOOK-03 — Add Book Listing:** Allow authenticated sellers to create book listings.

## File Responsibilities

| File | Responsibility |
|---|---|
| `apps.py` | Django application configuration |
| `models.py` | Book model and seller relationship |
| `forms.py` | Validation for book listing creation |
| `views.py` | Browse, search, and add-book request handling |
| `urls.py` | URL routes for book functionality |
| `admin.py` | Register the Book model in Django admin |
| `tests.py` | Tests for browsing, searching, validation, and access control |
| `migrations/` | Database migration files |
| `templates/books/book_list.html` | Book browsing page |
| `templates/books/book_search.html` | Search results page |
| `templates/books/book_form.html` | Seller listing creation page |

## Integration Dependencies

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

The templates currently provide basic functional HTML. They are not the final shared UI design.

When the team establishes the shared base template, navigation, and message-display conventions, these templates should be updated to follow them.

## Current Implementation Notes

- The templates are initial functional placeholders.
- Authentication and role checks depend on the shared Accounts implementation.
- Database migrations must be generated after the Django project settings and custom User model are configured.
- Tests must be run and updated against the integrated project before the pull request is considered complete.

## Scope Boundaries

This module covers book browsing, searching, and seller listing creation. It does not implement cart operations, order processing, payment processing, or other functionality assigned to separate modules.