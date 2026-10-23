from django.urls import include, path

from accounts.views import home


urlpatterns = [
    path("", home, name="home"),
    path("", include("accounts.urls")),
]
