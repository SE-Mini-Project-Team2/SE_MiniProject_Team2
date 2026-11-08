# System Validation Report

## 1. Overview

This document presents the system-level validation and integration testing performed for the Online Bookstore application.

The objective of system validation is to verify that the implemented modules work correctly together and satisfy the functional, security, authorization, and integration requirements defined in the Software Requirements Specification (SRS) and Software Test Plan (STP).

---

## 2. Scope

The following areas were validated:

- Customer registration and authentication
- Customer browsing and searching of books
- Shopping cart operations
- Order placement and order history
- Seller book listing
- Role-based access control
- Customer and seller workflow integration
- Security-related authorization behavior
- End-to-end interaction between application modules

The validation covers the system-level integration test cases IT-01 through IT-06.

---

## 3. Test Environment

| Item | Details |
|---|---|
| Application | Online Bookstore |
| Framework | Django |
| Database | PostgreSQL |
| Browser | Chrome |
| Operating System | Windows |
| Python Environment | Project `.venv` |
| Server | Django development server |
| Testing Type | System and Integration Testing |

---

## 4. System Validation Test Cases

### IT-01: Customer Registration and Login

**Objective:**  
Verify that a new customer can register successfully and subsequently authenticate using the registered credentials.

**Procedure:**

1. Open the Online Bookstore.
2. Navigate to the registration page.
3. Enter valid customer details.
4. Submit the registration form.
5. Log in using the registered credentials.
6. Verify that the customer is authenticated and can access customer functionality.

**Expected Result:**  
The customer account is created successfully, login succeeds, and the authenticated customer can access customer-specific functionality.

**Actual Result:**  
Customer registration and login completed successfully.

**Status:** PASS

---

### IT-02: Browse and Search Books

**Objective:**  
Verify that customers can browse available books and search for books using the bookstore search functionality.

**Procedure:**

1. Open the bookstore.
2. Navigate to the books page.
3. Verify that available books are displayed.
4. Enter a valid search term.
5. Submit the search.
6. Verify that matching books are displayed.

**Expected Result:**  
Books are displayed correctly and the search operation returns the relevant matching books.

**Actual Result:**  
Books were displayed successfully and the search functionality returned the expected results.

**Status:** PASS

---

### IT-03: Customer Cart Workflow

**Objective:**  
Verify that an authenticated customer can add books to the cart, manage cart contents through the supported operations, and proceed to order placement.

**Procedure:**

1. Log in as a Customer.
2. Browse the available books.
3. Add an available book to the cart.
4. Open the shopping cart.
5. Verify that the selected book is displayed with its quantity, current price, line total, and cart total.
6. Add the same book again.
7. Verify that the existing cart-line quantity increases.
8. Continue adding the same book until the quantity reaches 10.
9. Attempt to add the same book once more.
10. Verify that the quantity remains at 10 and an appropriate error message is displayed.
11. Remove the selected book from the cart.
12. Verify that the book is removed.

**Expected Result:**

- The book is added to the customer's cart with quantity 1.
- Adding the same book again increases the existing quantity rather than creating another cart line.
- The quantity does not exceed 10.
- An attempt to exceed the maximum quantity leaves the cart unchanged and displays an error message.
- The customer can remove the book from their own cart.
- Cart totals are calculated correctly.

**Actual Result:**  
The cart workflow completed successfully. Books were added to the cart, duplicate additions increased the existing quantity, the maximum quantity of 10 was enforced, and attempting to add an 11th copy displayed the appropriate error message. The book was also removed successfully from the cart.

**Status:** PASS

---

### IT-04: Customer Order Workflow

**Objective:**  
Verify that a customer can place an order using books present in their cart and subsequently view the order in order history.

**Procedure:**

1. Log in as a Customer.
2. Add an available book to the cart.
3. Verify the cart contents and total.
4. Proceed with order placement.
5. Verify that the order is created successfully.
6. Navigate to order history.
7. Verify that the newly placed order is displayed.

**Expected Result:**  
The order is created successfully using the cart contents, the order total is correct, and the order appears in the customer's order history.

**Actual Result:**  
The order workflow completed successfully and the placed order was available in the customer's order history.

**Status:** PASS

---

### IT-05: Seller Book Listing Workflow

**Objective:**  
Verify that an authenticated Seller can add a new book listing and that the listing becomes available in the bookstore.

**Procedure:**

1. Log in as a Seller.
2. Navigate to the seller book-listing functionality.
3. Enter valid book details.
4. Submit the book listing.
5. Verify that the book is created successfully.
6. Browse or search the bookstore.
7. Verify that the newly added book is available.

**Expected Result:**  
The Seller can successfully create a book listing and the newly created book is available through the bookstore.

**Actual Result:**  
The Seller book-listing workflow completed successfully and the newly created book was available through the bookstore.

**Status:** PASS

---

### IT-06: Role-Based Access Control

**Objective:**  
Verify that customer and seller permissions are enforced according to the defined role-based access rules.

**Procedure:**

1. Access the application as an unauthenticated user.
2. Verify access to publicly available book browsing functionality.
3. Log in as a Customer.
4. Verify that the Customer can access cart and order functionality.
5. Verify that the Customer cannot access Seller-only book-listing functionality.
6. Log in as a Seller.
7. Verify that the Seller can access book-listing functionality.
8. Verify that the Seller cannot access Customer-only cart and order functionality.
9. Verify that protected resources reject unauthorized access.

**Expected Result:**

- Public functionality is available without authentication where permitted.
- Customers can access customer-specific functionality.
- Sellers can access seller-specific functionality.
- Customers cannot perform seller-only operations.
- Sellers cannot perform customer-only cart/order operations.
- Unauthorized requests are rejected without modifying protected data.

**Actual Result:**  
Role-based access restrictions were enforced correctly. Customer and Seller permissions were separated according to the defined access rules.

**Status:** PASS

---

## 5. System Validation Summary

| Test Case | Validation Area | Status |
|---|---|---|
| IT-01 | Customer Registration and Login | PASS |
| IT-02 | Browse and Search Books | PASS |
| IT-03 | Customer Cart Workflow | PASS |
| IT-04 | Customer Order Workflow | PASS |
| IT-05 | Seller Book Listing Workflow | PASS |
| IT-06 | Role-Based Access Control | PASS |

### Overall Result

- **Total system validation tests:** 6
- **Executed:** 6
- **Passed:** 6
- **Failed:** 0
- **Blocked:** 0
- **Not Executed:** 0
- **Pass Rate:** 100%

---

## 6. Security and Authorization Validation

Security-related system behavior was also verified during system validation.

### Authentication

- Customer registration and login operate correctly.
- Invalid authentication attempts do not expose sensitive account information.
- Protected customer functionality requires authentication.

### Authorization

- Customer-only functionality is restricted to Customers.
- Seller-only functionality is restricted to Sellers.
- Users cannot access another customer's protected cart or order data.
- Unauthorized access attempts are rejected.

### Cart Security

- Cart operations are associated with the authenticated Customer.
- A Customer cannot remove another customer's cart item.
- Cart quantity limits are enforced.
- Cart modifications are performed through authenticated requests.

### Order Security

- Customer order functionality requires authentication.
- Customer-specific order information is protected from unauthorized access.

### Input and Request Protection

- Protected POST operations use CSRF protection.
- Invalid or unauthorized requests do not result in unauthorized data modification.
- Application error handling does not intentionally expose sensitive internal information.

---

## 7. Integration Validation

The following module interactions were validated as part of the end-to-end workflows:

| Integration | Validation |
|---|---|
| Authentication → Customer functionality | PASS |
| Authentication → Seller functionality | PASS |
| Books → Cart | PASS |
| Cart → Orders | PASS |
| Orders → Order History | PASS |
| Seller → Book Listing → Book Browsing | PASS |
| Role Authentication → Authorization | PASS |

The tests demonstrate that the major application modules operate together successfully rather than only functioning as isolated components.

---

## 8. Defect Summary

No system-level defects were identified during the executed IT-01 through IT-06 validation.

| Defect ID | Description | Severity | Status |
|---|---|---|---|
| None | No system-level defects identified | — | — |

The absence of `+`/`−` quantity controls in the cart was **not recorded as a defect**, because the SRS requires the quantity to increase when the same book is added again; it does not require manual quantity adjustment controls on the cart page.

---

## 9. Requirements Validation

The system validation confirmed the following major requirement areas:

- Customer authentication
- Book browsing and searching
- Cart creation and management
- Duplicate-book quantity increment
- Cart quantity limit
- Cart item removal
- Cart total calculation
- Customer order placement
- Order history
- Seller book listing
- Customer/Seller role separation
- Protected customer and seller functionality

These behaviors were validated through the corresponding system and integration workflows.

---

## 10. Conclusion

System-level validation of the Online Bookstore was completed using test cases IT-01 through IT-06.

All six system validation test cases passed. Customer, Seller, authentication, book, cart, order, and authorization workflows were successfully integrated and validated.

The validation results indicate that the implemented system satisfies the tested functional and authorization requirements defined for the project.