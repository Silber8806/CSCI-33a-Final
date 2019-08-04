from django.db import models
from django.contrib.auth.models import User

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

# Create your models here.

class Loan(models.Model):
    user_fk = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=256)
    loan_type = models.CharField(max_length=256)
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    terms = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=5)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

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


class Payment_Schedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    Payment_type = models.CharField(max_length=256)
    payment_date = models.DateTimeField()

    def __str__(self):
        return f"{self.id}"
