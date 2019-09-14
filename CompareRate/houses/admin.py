from django.contrib import admin

# customer tables
from .models import (
    Address
)

admin.site.register(Address)