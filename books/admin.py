from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "price", "seller")
    search_fields = ("title", "author")
    list_filter = ("seller",)
    ordering = ("title",)