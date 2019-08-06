from django.urls import path, re_path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('zipcode/', views.zipcode, name="zipcode"),
    path("house/<int:house_id>", views.house, name="house"),
]