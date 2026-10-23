from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.core.paginator import Paginator

from accounts.decorators import role_required
from .forms import BookForm
from .models import Book


BOOKS_PER_PAGE = 20
MAX_SEARCH_LENGTH = 100


def book_list(request):
    """FR-BOOK-01: Public, paginated book browsing."""
    books = Paginator(
        Book.objects.select_related("seller").all(),
        BOOKS_PER_PAGE,
    ).get_page(request.GET.get("page"))

    return render(request, "books/book_list.html", {"books": books})


def book_search(request):
    """FR-BOOK-02: Case-insensitive partial search by title or author."""
    query = request.GET.get("q", "").strip()

    if len(query) > MAX_SEARCH_LENGTH:
        return HttpResponseBadRequest(
            "Search text must not exceed 100 characters."
        )

    results = Book.objects.none()

    if query:
        from django.db.models import Q

        results = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        ).select_related("seller")

    books = Paginator(results, BOOKS_PER_PAGE).get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "books/book_search.html",
        {
            "books": books,
            "query": query,
        },
    )


@role_required("SELLER")
def add_book(request):
    """FR-BOOK-03: Only authenticated sellers may create listings."""
    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            book = form.save(commit=False)
            book.seller = request.user
            book.save()

            messages.success(request, "Book listing added successfully.")
            return redirect("books:list")
    else:
        form = BookForm()

    return render(request, "books/book_form.html", {"form": form})