from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F

from .models import Loan

# Create your views here.

@login_required(login_url='/accounts/login/')
def index(request):
    current_loans = Loan.objects.filter(user_fk=request.user.id)
    principal_total = current_loans.aggregate(Sum('principal'))
    average_interest = current_loans.aggregate(sum=100 * Sum(F('principal')*F('interest_rate'))/Sum('principal'))["sum"]
    total_cash_outflow = sum([loan.monthly_payment for loan in current_loans])

    context = {
        "loans": current_loans,
        "total_principal": principal_total,
        "average_interest": average_interest,
        "total_payments": total_cash_outflow
    }
    return render(request, 'liabilities/index.html', context)