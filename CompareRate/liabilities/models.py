from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Loan(models.Model):
    user_fk = models.ForeignKey(User,on_delete=models.CASCADE)
    provider = models.CharField(max_length=256)
    principal = models.DecimalField(max_digits=12, decimal_places=2)
    terms = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=5)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True,null=True)

    @property
    def interest_payment(self):
        return round(float(self.principal) * float(self.interest_rate) / 12.0, 2)

    @property
    def periodic_period(self):
        return round(self.principal * (
                (self.interest_rate / 12.0 * (1 + self.interest_rate / 12.0) ** self.terms) / (
                (1 + self.interest_rate / 12.0) ** self.terms - 1)), 2)

    def __str__(self):
        return f"{self.id} - {self.provider} - ${self.principal} - {self.terms} months"


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    Payment_type = models.CharField(max_length=256)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"


class Payment_Schedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    Payment_type = models.CharField(max_length=256)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}"
