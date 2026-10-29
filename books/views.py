
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render

from accounts.decorators import role_required
from .forms import BookForm
from .models import Book


BOOKS_PER_PAGE = 20
MAX_SEARCH_LENGTH = 100


def book_list(request):
    """Display a paginated list of available books."""

    books = Paginator(
        Book.objects.select_related("seller").all(),
        BOOKS_PER_PAGE,
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "books/book_list.html",
        {"books": books},
    )


def book_search(request):
    """Search for books by title or author."""

    query = request.GET.get("q", "").strip()

    if len(query) > MAX_SEARCH_LENGTH:
        return HttpResponseBadRequest(
            "Search text must not exceed 100 characters."
        )

    results = Book.objects.none()

    if query:
        results = Book.objects.filter(
            Q(title__icontains=query)
            | Q(author__icontains=query)
        ).select_related("seller")

    books = Paginator(
        results,
        BOOKS_PER_PAGE,
    ).get_page(request.GET.get("page"))

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
    """Allow authenticated sellers to create book listings."""

    if request.method == "POST":
        form = BookForm(request.POST)

        if form.is_valid():
            book = form.save(commit=False)

            # Associate the listing with the logged-in seller.
            book.seller = request.user
            book.save()

            messages.success(
                request,
                "Book listing added successfully.",
            )

            return redirect("books:list")

    else:
        # Prefill the title from a search query, if provided.
        initial_data = {}

        title = request.GET.get("title", "").strip()

        if title:
            if len(title) > MAX_SEARCH_LENGTH:
                return HttpResponseBadRequest(
                    "Book title must not exceed 100 characters."
                )

            initial_data["title"] = title

        form = BookForm(initial=initial_data)

    return render(
        request,
        "books/book_form.html",
        {"form": form},
    )
