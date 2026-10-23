
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from books.models import Book
from .models import CartItem


@login_required
def view_cart(request):
    items = CartItem.objects.filter(
        customer=request.user
    ).select_related("book")

    total = sum(item.line_total for item in items)

    return render(
        request,
        "cart/cart_detail.html",
        {"items": items, "total": total},
    )


@login_required
def add_to_cart(request, book_id):
    if request.method != "POST":
        return redirect("cart:view_cart")

    book = get_object_or_404(Book, pk=book_id)

    item = CartItem.objects.filter(
        customer=request.user,
        book=book,
    ).first()

    if item:
        if item.quantity >= 10:
            messages.error(
                request,
                "You can add a maximum of 10 copies of a book."
            )
        else:
            item.quantity += 1
            item.save(update_fields=["quantity"])
            messages.success(request, "Cart quantity updated.")
    else:
        CartItem.objects.create(
            customer=request.user,
            book=book,
            quantity=1,
        )
        messages.success(request, "Book added to your cart.")

    return redirect("cart:view_cart")


@login_required
def remove_from_cart(request, item_id):
    if request.method != "POST":
        return redirect("cart:view_cart")

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        customer=request.user,
    )
    item.delete()
    messages.success(request, "Book removed from your cart.")

    return redirect("cart:view_cart")
