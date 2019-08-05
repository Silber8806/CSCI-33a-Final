from django.db import models
from django.contrib.auth.models import User

from datetime import date
from django.db.models import Sum, F

# Create your models here.

class Loan_Type(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.name}"

class Loan(models.Model):
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=256)
    loan_type = models.ForeignKey(Loan_Type,on_delete=models.DO_NOTHING)
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    terms = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=5)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=256, default="active")

    def _get_latest_payment(self):
        return Payment.objects.filter(loan=self).filter(payment_date__gt=date.today()).order_by('installment').first()

    @property
    def interest_rate_pct(self):
        return round(100 * self.interest_rate, 3)

    @property
    def periodic_interest_rate(self):
        return float(self.interest_rate) / 12.0

    @property
    def loan_cost(self):
        return (int(self.terms) * (float(self.principal) * self.periodic_interest_rate) / (
                1 - (1 + self.periodic_interest_rate) ** (-1 * int(self.terms)))) - float(self.principal)

    @property
    def monthly_payment(self):
        return float(self.principal) * (
                    self.periodic_interest_rate * (1 + self.periodic_interest_rate) ** int(self.terms)) / (
                           (1 + self.periodic_interest_rate) ** int(self.terms) - 1)

    @property
    def last_principal_payment(self):
        last_payment = self._get_latest_payment()
        return last_payment.principal_paid + last_payment.addition_paid

    @property
    def last_interest_payment(self):
        return self._get_latest_payment().interest_paid

    @property
    def current_principal(self):
        return self._get_latest_payment().principal_base

    def __str__(self):
        return f"{self.user_fk.username} - {self.provider} - ${self.principal} - {self.terms} months"


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    installment = models.IntegerField()
    payment_type = models.CharField(max_length=256)
    payment_date = models.DateField()
    principal_base = models.DecimalField(max_digits=12, decimal_places=2)
    principal_paid = models.DecimalField(max_digits=12, decimal_places=2)
    addition_paid = models.DecimalField(max_digits=12, decimal_places=2)
    interest_paid = models.DecimalField(max_digits=12, decimal_places=2)
    total_paid = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.installment} - {self.loan}"