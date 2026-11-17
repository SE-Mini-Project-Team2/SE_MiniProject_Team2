from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.book_list, name="list"),
    path("search/", views.book_search, name="search"),
    path("add/", views.add_book, name="add"),
    path("mine/", views.my_listings, name="my_listings"),
]