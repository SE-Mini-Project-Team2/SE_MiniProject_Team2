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

- The Books module provides book browsing, searching, and seller listing creation.
- The homepage and book pages provide navigation to the browsing and search features.
- Search supports case-insensitive partial matches against book titles and authors.
- Search results handle empty queries and searches with no matching books.
- Authenticated sellers can access the book-listing form.
- The search page provides sellers with a direct option to start a new listing.
- When a seller starts a listing from a search query, the book title can be prefilled.
- The seller is associated with the listing on the server side.
- Book listings are saved through Django's ORM.
- Customers must not be able to create listings, even by accessing the add-book URL directly.
- Templates use the shared Accounts implementation for authentication and role checks.
- Tests should verify browsing, searching, seller listing creation, customer restrictions, and database persistence.

## Book Routes

| Route | Purpose | Access |
|---|---|---|
| `/books/` | Browse available books | Public |
| `/books/search/?q=<query>` | Search by title or author | Public |
| `/books/add/` | Create a book listing | Authenticated sellers only |

The add-book form can accept a title through the `title` query parameter to prefill the title field when starting a listing from a search.

## Verification Checklist

- [ ] Books appear on the listing page.
- [ ] Search returns matching books.
- [ ] Searches with no matches display an appropriate message.
- [ ] Sellers can access the add-book form.
- [ ] The search query can prefill the new listing's title.
- [ ] Customers cannot create book listings.
- [ ] Successfully submitted listings remain saved in the database.
- [ ] The newly created book appears in the listing.

## Scope Boundaries

This module covers book browsing, searching, and seller listing creation. It does not implement cart operations, order processing, payment processing, or other functionality assigned to separate modules.