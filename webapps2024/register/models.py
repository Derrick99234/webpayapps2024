from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserInfo(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default=None)
  balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)  # Assuming initial amount
  currency = models.CharField(max_length=3, choices=[('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='USD')

  def __str__(self):
    return f"{self.user.username} - {self.currency}"


