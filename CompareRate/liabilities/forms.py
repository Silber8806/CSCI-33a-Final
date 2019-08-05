from django import forms
from django.conf import settings

from .models import Loan

class LoanForm(forms.ModelForm):

    class Meta:
        model = Loan
        fields = ('provider', 'loan_type','principal','terms','interest_rate','start_date')

