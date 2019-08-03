import locale

from django.contrib import admin

# customer tables
from .models import (
    Loan
)

locale.setlocale( locale.LC_ALL, '' )

class LoanAdmin(admin.ModelAdmin):
    list_display = ('provider', 'loan_type', 'principal_dollars','terms','interest_rate_100','start_date','end_date')
    list_filter = ('provider', 'loan_type')

    def interest_rate_100(self,obj):
        return str(round(obj.interest_rate * 100,3)) + "%"

    def principal_dollars(self,obj):
        return locale.currency(obj.principal, grouping=True)

admin.site.register(Loan, LoanAdmin)