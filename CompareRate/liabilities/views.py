from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F

from .models import Loan
from .forms import LoanForm

# Create your views here.

@login_required(login_url='/accounts/login/')
def index(request):
    current_loans = Loan.objects.filter(user_fk=request.user.id)
    principal_total = current_loans.aggregate(Sum('principal'))
    total_cost = sum(loan.loan_cost for loan in current_loans)
    average_interest = current_loans.aggregate(sum=100 * Sum(F('principal')*F('interest_rate'))/Sum('principal'))["sum"]
    total_cash_outflow = sum([loan.monthly_payment for loan in current_loans])

    context = {
        "loans": current_loans,
        "total_principal": principal_total,
        "average_interest": average_interest,
        "total_payments": total_cash_outflow,
        "total_cost": total_cost
    }
    return render(request, 'liabilities/index.html', context)

@login_required(login_url='/accounts/login')
def detail(request,loan):
    loan = get_object_or_404(Loan,pk=loan)
    if request.method == "POST":
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user_fk = request.user
            loan.save()
            return redirect('detail',loan=loan.pk)
    else:
        form = LoanForm(instance=loan)
    return render(request,'liabilities/details.html',{'form':form})