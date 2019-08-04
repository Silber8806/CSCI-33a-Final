from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.http import QueryDict
from django.http import JsonResponse

from .models import Loan
from .forms import LoanForm

from dateutil.relativedelta import relativedelta
from django.db import transaction

from .models import Payment

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
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.user_fk = request.user
                loan.end_date = loan.start_date + relativedelta(months=loan.terms)
                loan.save()
                Payment.objects.filter(loan=loan).delete()
                balance=float(loan.principal)
                for term_number in range(loan.terms):
                    new_payment_interest = round(balance * float(loan.periodic_interest_rate), 2)
                    new_payment = Payment(
                            loan=loan,
                            installment=term_number+1,
                            payment_type='periodic',
                            payment_date=loan.start_date + relativedelta(term_number),
                            principal_base=balance,
                            principal_paid=loan.monthly_payment - new_payment_interest,
                            interest_paid=new_payment_interest,
                            total_paid=loan.monthly_payment,
                            addition_paid=0
                            )
                    balance = balance - (loan.monthly_payment - new_payment_interest)
                    new_payment.save()
                return redirect('detail',loan=loan.pk)
    else:
        loans = Loan.objects.filter(user_fk=request.user)
        form = LoanForm(instance=loan)
        context = {
            'form': form,
            'loans': loans,
            'active_loan': loan,
        }
    return render(request,'liabilities/details.html',context)

@login_required(login_url='/accounts/login')
def add_loan(request):
    if request.method == "POST":
        form = LoanForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                loan = form.save(commit=False)
                loan.user_fk = request.user
                loan.end_date = loan.start_date + relativedelta(months=loan.terms)
                print(loan.end_date)
                loan.save()
                balance=float(loan.principal)
                for term_number in range(loan.terms):
                    new_payment_interest = round(balance * float(loan.periodic_interest_rate), 2)
                    new_payment = Payment(
                            loan=loan,
                            installment=term_number+1,
                            payment_type='periodic',
                            payment_date=(loan.start_date + relativedelta(months=term_number)),
                            principal_base=balance,
                            principal_paid=loan.monthly_payment - new_payment_interest,
                            interest_paid=new_payment_interest,
                            total_paid=loan.monthly_payment,
                            addition_paid=0
                            )
                    balance = balance - (loan.monthly_payment - new_payment_interest)
                    new_payment.save()
            return redirect('detail',loan=loan.pk)
    else:
        loans = Loan.objects.filter(user_fk=request.user)
        form = LoanForm()
        context = {
            'form': form,
            'loans': loans
        }
    return render(request,'liabilities/details.html',context)

@login_required(login_url='/accounts/login')
def delete_loan(request):
    if request.method == "DELETE":
        loan_to_delete = QueryDict(request.body).get('loan')
        with transaction.atomic():
            Payment.objects.filter(loan=loan_to_delete).delete()
            Loan.objects.get(pk=loan_to_delete).delete()
            payload = {'success': True}
            return JsonResponse(payload)
