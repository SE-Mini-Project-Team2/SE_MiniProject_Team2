from django.urls import include, path

from accounts.views import home

urlpatterns = [
    path("", home, name="home"),
    path("", include("accounts.urls")),
    path("books/", include("books.urls")),
    path("cart/", include("cart.urls")),
]