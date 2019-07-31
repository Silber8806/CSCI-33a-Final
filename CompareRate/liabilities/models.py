from django.db import models

# Create your models here.

class Loans(models.Model):
    loan_provider = models.CharField(max_length=256)
    loan_principal = models.DecimalField(max_digits=12, decimal_places=2)
    loan_terms = models.IntegerField()
    loan_interest_rate = models.DecimalField(max_digits=5, decimal_places=5)

    def interest_payment(self):
        return self.loan_principal * self.loan_interest_rate / 12

    def periodic_period(self):
        return math.round(self.loan_principal * (
                    (self.loan_interest_rate / 12.0 * (1 + self.loan_interest_rate / 12.0) ** self.loan_terms) / (
                    (1 + self.loan_interest_rate / 12.0) ** self.loan_terms - 1)), 2)

    def __str__(self):
        return f"{self.id} - {self.loan_provider} - ${self.loan_terms}"
