from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<int:loan>",views.detail,name="detail"),
    path("add_loan/",views.add_loan,name="add_loan"),
]