from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserInfo(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, default=None)
  balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)  # Assuming initial amount
  currency = models.CharField(max_length=3, choices=[('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='USD')

  def __str__(self):
    return f"{self.user.username} - {self.currency}"


class Request(models.Model):
  sender = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name="sent_requests")
  receiver = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name="received_requests")
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  STATUS_CHOICES = (
      ('pending', 'Pending'),
      ('accepted', 'Accepted'),
      ('rejected', 'Rejected')
  )
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
  timestamp = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Request: {self.sender} -> {self.receiver} - Amount: {self.amount} ({self.status})"


class Transaction(models.Model):
  sender = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='sent_transactions')
  recipient = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name='received_transactions')
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  sender_currency = models.CharField(max_length=3, choices=[('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='USD')
  STATUS_CHOICES = (
      ('pending', 'Pending'),
      ('completed', 'Completed'),
      ('cancelled', 'Cancelled'),
  )
  status = models.CharField(max_length=20, choices=STATUS_CHOICES)
  timestamp = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"Transaction: {self.sender} -> {self.recipient} - Amount: {self.amount} ({self.status})"


class Notification(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return f"Request: {self.user.user.username} -> {self.message}"