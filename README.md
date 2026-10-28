# Online Bookstore

## 1. Project Overview

The Online Bookstore is a web-based application developed using Python and Django. It allows users to browse and search for books, manage shopping carts, place orders, and view order history.

The system supports two registered roles:

- **Customer** – Can browse and search books, manage a shopping cart, place orders, and view their own order history.
- **Seller** – Can browse and search books and add book listings.

Unauthenticated users can register, log in, browse books, and search for books.

The application follows a **layered modular monolith** architecture with separate modules for authentication, book management, cart management, and order management.

## 2. Objectives

- Provide a platform for browsing and searching books.
- Allow Customers to manage shopping carts and place orders.
- Allow Customers to view their own order history.
- Allow Sellers to create book listings.
- Implement authentication and server-side role-based access control.
- Protect user data and prevent unauthorized access.
- Maintain consistent cart and order data.
- Provide a maintainable and testable application structure.

## 3. Technology Stack

- **Programming Language:** Python
- **Web Framework:** Django
- **Architecture:** Layered Modular Monolith
- **Database:** SQLite for development and demonstration; PostgreSQL if hosted
- **Data Access:** Django ORM
- **Frontend:** Django Templates, HTML, CSS, and optional JavaScript
- **Authentication:** Django Authentication and password hashing
- **Version Control:** Git and GitHub

## 4. Core Features

### Authentication

- User registration
- User login
- User logout
- Customer/Seller role selection during registration
- Server-side role validation

### Book Management

- Browse available books from the homepage or book listing page.
- Search books by title or author.
- Display matching results and handle searches with no results.
- Allow authenticated sellers to create book listings.
- Provide sellers with direct access to book creation from the search page.
- Prefill the book title from the search query when creating a listing.
- Restrict book-listing creation to sellers using server-side role checks.
- Save new book listings in the database.
- Associate each listing with the seller who created it.

### Shopping Cart

- Add books to the cart
- Increase quantity when the same book is added again
- Remove books from the cart
- View cart contents
- Quantity validation with a maximum of 10 per book

### Order Management

- Place orders from the cart
- Calculate order totals using server-side book prices
- View previously placed orders
- Maintain order and cart consistency using database transactions

## Homepage Navigation

The homepage provides navigation to the main bookstore features.

- **Browse Books:** Opens the book listing page.
- **Search Books:** Allows users to search by title or author.
- **Add a Book Listing:** Available to authenticated sellers only.
- **My Orders:** Provides access to the user's order history.
- **Log In / Register:** Available to users who are not authenticated.

Sellers can also start creating a book listing directly from the search page. When a seller chooses to add a book from a search query, the title can be prefilled in the listing form.

Server-side role checks remain responsible for preventing customers from creating book listings.

### Security

- Server-side role-based access control
- User-specific cart and order access
- Password hashing and validation
- CSRF protection
- Input validation and output escaping
- Server-side price and quantity validation
- Protection against unauthorized data access
- Safe error handling and logging

## 5. Architecture

The project uses a **layered modular monolith** implemented with Django.

The main application modules are:

```text
accounts/   - Registration, login, logout, authentication and roles
books/      - Book browsing, searching and seller listings
cart/       - Cart management and ownership checks
orders/     - Order placement, transactions and order history
templates/  - HTML templates and shared UI
tests/      - Unit, integration, permission and workflow tests
```

The application uses Django Models and the Django ORM for database access.

Microservices are not used because they are unnecessary for the current project scope.

## 6. Project Scope

### Included

- User registration, login and logout
- Book browsing and searching
- Seller book-listing creation
- Shopping cart management
- Order placement
- Order history
- Role-based access control
- User data protection
- Functional, security, usability, performance and compatibility testing

### Out of Scope

- Payment gateway processing
- Delivery tracking and courier integration
- Book reviews and ratings
- Wishlists
- Discounts
- Recommendations
- Seller payouts
- Inventory replenishment
- Editing or deleting book listings
- Administrator dashboards
- Mobile application

## 7. Database

SQLite is used for development and demonstration.

If the application is hosted, PostgreSQL will be used as the production database.

The application uses the Django ORM so that the database layer remains portable between these environments.

## 8. Security

Security is enforced at the server and database layers rather than relying only on frontend restrictions.

The project includes:

- Role-based access control
- Password hashing and password validation
- Secure session management
- CSRF protection
- Ownership checks for carts and orders
- Server-side price and quantity validation
- Atomic order creation
- Bounded and paginated search
- Safe logging
- Generic error handling
- Secure configuration for hosted environments

The security requirements are organized under:

- **SEC-01:** Role-Based Access
- **SEC-02:** Protection of User Data
- **SEC-CTRL-01 to SEC-CTRL-20:** Detailed security controls

`SEC-CTRL-16`, which covers login throttling, is an optional enhancement and is outside the mandatory acceptance baseline.

## 9. Testing

Testing is defined in the **Software Test Plan (STP)**.

The testing scope includes:

- Unit testing
- Integration testing
- System testing
- Functional testing
- Security testing
- Performance testing
- Usability testing
- Browser compatibility testing
- Regression testing
- Data consistency testing

The current test plan contains **27 test cases** and **6 integration test scenarios**.

## 10. Project Documentation

The project documentation consists of the following documents:

1. **Software Requirements Specification (SRS)**  
   Defines the functional, non-functional, security and business requirements.

2. **Software Architecture and Design Specification (SAD)**  
   Defines the system architecture, components, data model, interfaces and implementation design.

3. **Software Test Plan (STP)**  
   Defines the testing strategy, test cases, traceability and verification approach.

4. **Security & Integration Plan**  
   Defines the security objectives, security controls and integration plan.

All four documents are maintained as **Version 1.1 Final** and are synchronized with each other. The **SRS is the authoritative requirements baseline**.

## 11. Project Status

| Area | Status |
|---|---|
| Requirements Documentation | Completed – Version 1.1 Final |
| Architecture | Defined |
| Database | SQLite for development/demo; PostgreSQL if hosted |
| Security Requirements | Finalized |
| Testing Plan | Finalized |
| Implementation | In Progress |
| Deployment Environment | To be finalized |

## 12. Setup Instructions

The initial Django project and Accounts module are configured for local development with SQLite.

From the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo_data # for creating the dataset on user side for now 
python manage.py runserver
```

Run the authentication tests with:

```powershell
python manage.py test accounts
```

The local development secret and debug settings have safe development defaults. Set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=False` and configure allowed hosts before deploying; the default settings are not a production deployment configuration.

## 13. Project Structure

The planned Django project structure is:

```text
Online-Bookstore/
│
├── README.md
├── documentation/
│   ├── SRS
│   ├── SAD
│   ├── STP
│   └── Security & Integration Plan
│
├── accounts/
├── config/
├── books/
├── cart/
├── orders/
├── templates/
├── tests/
├── requirements.txt
└── manage.py
```

The exact implementation structure may be adjusted during development while preserving the module responsibilities defined in the architecture.

## 14. Team

Developed collaboratively by **Team 2 – Online Bookstore Project**.

### Team Members

- **M1 – Pooja Avadhani**
- **M2 – Rahul M S**
- **M3 – Preksha B**
- **M4 – Ojas Binjola**

## 15. Version

**Current Documentation Version:** 1.1 Final

**Project:** Online Bookstore  
**Team:** Team 2  
**Institution:** PES University, Bengaluru  
**Department:** Computer Science and Engineering