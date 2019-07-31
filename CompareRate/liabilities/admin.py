from django.contrib import admin

# customer tables
from .models import (
    Loan
)

admin.site.register(Loan)