from django.urls import path

from . import views

urlpatterns = [
    path("house_search", views.house_search, name="house_search"),
]