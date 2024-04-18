from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    balance = models.IntegerField()
    currency = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

