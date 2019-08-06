from django.contrib import admin

# customer tables
from .models import (
    ZipCodes
)

admin.site.register(ZipCodes)