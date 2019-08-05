from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<int:loan>",views.detail,name="detail"),
    path("add_loan/",views.add_loan,name="add_loan"),
    path("delete_loan/",views.delete_loan,name="delete_loan"),
    path("payment_schedule/<int:loan>",views.payment_schedule,name="payment_schedule"),
]