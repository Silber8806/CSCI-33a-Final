from django.db import models

# Create your models here.
class Address(models.Model):
    longitude = models.DecimalField(max_digits=10,decimal_places=7)
    latitude = models.DecimalField(max_digits=9,decimal_places=7)
    street = models.CharField(max_length=512)
    city = models.CharField(max_length=256)
    state = models.CharField(max_length=2)
    zipcode = models.IntegerField()

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zipcode}"
