from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserInfo, Request, Transaction, Notification
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.exceptions import ValidationError  # For currency validation
from django.contrib.auth import logout
from decimal import Decimal
import logging
import json
# from django.dispatch import receiver
# from django.contrib.auth.signals import user_logged_in    
# from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.
def home(request):
    return render(request, 'index.html')

def send_transaction_notification(sender, recipient, message):
    Notification.objects.create(user=sender, message=message)
    Notification.objects.create(user=recipient, message=message)

# @receiver(user_logged_in)
# def send_login_notification(sender, user, request, **kwargs):
#     message = "Welcome back! You have successfully logged in."
#     Notification.objects.create(user=user, message=message)

def signin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        userInfo = UserInfo.objects.get(user=user)

        if user is not None:
            login(request, user)

            messages.success(request, "Login successful.")
            # send_login_notification(sender=None, user=userInfo, request=request)
            # send_transaction_notification(user, recipient_info.user, "You have received money from...")
            return redirect('dashboard', pk=user.pk, username=username)
        else:
            messages.error(request, "Login credentials are incorrect.")
            return render(request, 'authentication/login.html')

    return render(request, 'authentication/login.html')


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        fname = request.POST['fname']
        lname = request.POST['lname']
        currency = request.POST['currency']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
                messages.error(request, "Passwords do not match")
                return render(request, 'authentication/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'authentication/register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return render(request, 'authentication/register.html')

        # Set initial amount based on currency
        initial_amount = 0
        if currency == 'USD':
            initial_amount = 100  # Example initial amount for USD
        elif currency == 'EUR':
            initial_amount = 90   # Example initial amount for EUR
        elif currency == 'GBP':
            initial_amount = 80   # Example initial amount for GBP

        myuser = User.objects.create_user(username=username, email=email, password=password1);
        
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()

        UserInfo.objects.create(
            user = myuser,
            currency = currency,
            balance = initial_amount,
        )

        messages.success(request, "Account created successfully. You can now login.")

        return redirect('login')

    return render(request, 'authentication/register.html')

class SendMoneyForm(forms.Form):
    amount = forms.FloatField(min_value=0.01, required=True) 
    email = forms.EmailField(required=True)

def dashboard(request, pk, username):
    # user = User.objects.get(pk=pk)
    userInfo = UserInfo.objects.get(pk=pk)
    
    context = {
            "username" : userInfo.user.username,
            "balance" : userInfo.balance,
            "currency" : userInfo.currency,
        }
    return render(request, "dashboard.html", context)

def logout_view(request):
  logout(request)
  messages.success(request, "You have been logged out successfully.")
  return redirect('login') 

def convert_currency(amount, from_currency, to_currency):
  conversion_rates = {
      "GBP": {"USD": 1.30, "EUR": 1.15},  # Example rates
      "EUR": {"USD": 1.10, "GBP": 0.87},  # Example rates
      "USD": {"EUR": 0.91, "GBP": 0.77},  # Example rates
  }

  if from_currency != to_currency and to_currency in conversion_rates[from_currency]:
    return amount * conversion_rates[from_currency][to_currency]
  else:
    intermediate_currency = "USD"  # You can choose a different intermediate currency
    converted_to_intermediate = amount * conversion_rates[from_currency][intermediate_currency]
    converted_to_target = converted_to_intermediate * conversion_rates[intermediate_currency][to_currency]
    return converted_to_target



@login_required
def send_money(request):
    sender = User.objects.get(username=request.user)
    sender_info = UserInfo.objects.get(user=sender)

    if request.method == "POST":
        amount = request.POST.get("amount")
        recipient_email = request.POST.get("email")

        # Validate amount
        if not amount.isdigit() or float(amount) <= 0:
            messages.error(request, "Invalid amount. Please enter a positive number.")
            return render(request, 'send_money.html')

        try:
            recipient = User.objects.get(email=recipient_email)
            recipient_info = UserInfo.objects.get(user=recipient)
            recipient_currency = recipient_info.currency
        except User.DoesNotExist:
            messages.error(request, "Recipient with this email address not found.")
            return render(request, 'send_money.html')

        # Check sender's balance
        if sender_info.balance < float(amount):
            messages.error(request, "Insufficient funds. Please top up your balance.")
            return render(request, 'send_money.html')

        # Check sender and recipient currencies
        valid_currencies = ["GBP", "EUR", "USD"]
        if sender_info.currency not in valid_currencies:
            raise ValidationError(f"Invalid sender currency: {sender_info.currency}")
        if recipient_currency and recipient_currency not in valid_currencies:
            raise ValidationError(f"Invalid recipient currency: {recipient_currency}")

        # Convert amount if sender and recipient have different currencies
        if sender_info.currency != recipient_currency and recipient_currency:
            converted_amount = convert_currency(float(amount), sender_info.currency, recipient_currency)
        else:
            converted_amount = float(amount)

        # Perform money transfer
        sender_info.balance -= Decimal(amount)
        recipient_info.balance += Decimal(converted_amount)
        sender_info.save()
        recipient_info.save()

        all_transactions = Transaction.objects.create(
          sender = sender_info,
          recipient = recipient_info,
          status = "completed",
          amount = Decimal(amount),
          sender_currency = sender_info.currency
        )
        all_transactions.save()
        send_transaction_notification(sender=sender_info, recipient=recipient_info, message=f"{sender_info.user.username} sent {amount} to {recipient_info.user.username} status: completed")

        messages.success(request, f"Successfully sent {amount} {sender_info.currency} to {recipient.email}.")
        
        return redirect('dashboard', pk=request.user.pk, username=request.user.username)

    context = {
        "username": sender_info.user.username,
        "balance": sender_info.balance,
        "currency": sender_info.currency,
        "email": sender_info.user.email,
    }
    return render(request, 'makePayments.html', context)


def request_money(request):
  if request.method == "POST":
    recipient_email = request.POST.get("email")
    amount = request.POST.get("amount")

    if amount is None or amount == "":
      messages.error(request, "Invalid amount. Please enter a positive number.")
      messages_json = json.dumps([str(message) for message in messages])
      return render(request, 'makePayments.html',{'messages': messages, 'messages_json': messages_json})

    if not amount.isdigit() or float(amount) <= 0:
      messages.error(request, "Invalid amount. Please enter a positive number.")
      messages_json = json.dumps([str(message) for message in messages])
      return render(request, 'makePayments.html', {'messages': messages, 'messages_json': messages_json})
    
    try:
      recipient = User.objects.get(email=recipient_email)
      sender_user_info = UserInfo.objects.get(user=request.user)
      recipient_user = UserInfo.objects.get(user=recipient)
    except User.DoesNotExist:
      messages.error(request, "Recipient with this email address not found.")
      messages_json = json.dumps([str(message) for message in messages])
      return render(request, 'makePayments.html', {'messages': messages, 'messages_json': messages_json})

    # Create and save the request object
    request_obj = Request.objects.create(
        sender=sender_user_info,
        receiver=recipient_user,
        amount=float(amount),
        status="pending"
    )
    request_obj.save()
    all_transactions = Transaction.objects.create(
          sender = recipient_user,
          recipient = sender_user_info,
          status = "pending",
          amount = Decimal(amount),
          sender_currency = sender_user_info.currency
    )
    all_transactions.save()
    send_transaction_notification(sender=recipient_user, recipient=sender_user_info, message=f"{sender_user_info.user.username} requested {amount} from {recipient_user.user.username} status: pending")

    messages.success(request, f"Successfully requested {amount} from {recipient.email}.")
    return redirect('dashboard', pk=request.user.pk, username=request.user)

  return render(request, 'makePayments.html', {'messages': messages, 'messages_json': messages_json})


@login_required
def pending_requests(request):
    userInfo = UserInfo.objects.get(user=request.user)
    pending_requests = Request.objects.filter(receiver=userInfo, status="pending")
    context = {
      'pending_requests': pending_requests,
    }
    logging.debug(pending_requests)
    return render(request, 'money_request.html', context)


@login_required
def accept_request(request, pk):
    try:
        request_obj = Request.objects.get(pk=pk)
        
        sender = request_obj.sender
        receiver = request_obj.receiver
        amount = request_obj.amount

        if receiver.balance < amount:
            messages.error(request, f"Failed to accept request. {sender.user.username} doesn't have sufficient funds.")
            return redirect('pending_requests')
        if sender.currency != receiver.currency and receiver.currency:
            converted_amount = convert_currency(float(amount), sender.currency, receiver.currency)
        else:
            converted_amount = float(amount)
        
        # Update balances
        receiver.balance -= Decimal(amount)
        sender.balance += Decimal(converted_amount)
        
        # Save changes to both sender and receiver
        receiver.save()
        sender.save()
        
        # Update request status
        request_obj.status = "accepted"
        request_obj.save()
        transaction_obj = Transaction.objects.get(sender=receiver, recipient=sender, amount=amount)
        transaction_obj.status = "completed"
        transaction_obj.save()
        
        # Redirect to dashboard with sender's user ID
        messages.success(request, f"Successfully accepted request from {request_obj.sender.user.username}.")
        send_transaction_notification(sender=sender, recipient=receiver, message=f"{receiver.user.username} accepted {sender.user.username} request of {amount}")
        return redirect('dashboard', pk=request.user.pk, username=request.user)
    
    except Request.DoesNotExist:
        return render(request, 'error.html', context={'message': 'Request not found.'})


@login_required
def reject_request(request, pk):
  try:
    request_obj = Request.objects.get(pk=pk)
    amount = request_obj.amount
    request_obj.status = "rejected"
    request_obj.save()

    transaction_obj = Transaction.objects.filter(sender=request_obj.receiver, recipient=request_obj.sender, amount=amount).latest('timestamp')

    transaction_obj.status = "cancelled"
    transaction_obj.save()
    send_transaction_notification(sender=request_obj.receiver, recipient=request_obj.sender, message=f"{request_obj.sender.user.username} rejected {request_obj.receiver.user.username} request of {amount}")

    messages.success(request, f"Successfully rejected request from {request_obj.sender.user. username}.")
    return redirect('dashboard', pk=request.user.pk, username=request.user)
  except Request.DoesNotExist:
    return render(request, 'error.html', context={'message': 'Request not found.'})
  
def all_transactions(request):
    user = request.user
    userInfo = UserInfo.objects.get(user=user)
    transactions = Transaction.objects.filter(sender=userInfo) | Transaction.objects.filter(recipient=userInfo).order_by('-timestamp')
    context = {'transactions': transactions}
    return render(request, 'all_transactions.html', context)


@login_required
def view_notifications(request):
    userInfo = UserInfo.objects.get(user=request.user)
    notifications = Notification.objects.filter(user=userInfo).order_by("-created_at")

    return render(request, "notification.html", {"notifications": notifications})