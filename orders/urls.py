from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("", views.order_history, name="history"),
    path("place/", views.place_order_view, name="place"),
]
