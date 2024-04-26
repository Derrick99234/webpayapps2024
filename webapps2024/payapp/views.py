from django.shortcuts import render
from .models import UserInfo, Request, Transaction, Notification
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from decimal import Decimal
import logging
import json
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
import requests

# Create your views here.


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


def send_transaction_notification(sender, recipient, message):
    Notification.objects.create(user=sender, message=message)
    Notification.objects.create(user=recipient, message=message)



def convert_currency(request, currency1, currency2, amount_of_currency1):
    conversion_rates = {
        "USD": {"EUR": 0.85, "GBP": 0.73},
        "EUR": {"USD": 1.18, "GBP": 0.86},
        "GBP": {"USD": 1.37, "EUR": 1.16},
    }

    try:
        amount_of_currency1 = float(amount_of_currency1)
    except ValueError:
        return JsonResponse({'error': 'Invalid amount'})

    # Check if the currencies are supported
    if currency1 not in conversion_rates or currency2 not in conversion_rates[currency1]:
        return JsonResponse({'error': 'Invalid currency conversion'})

    # Calculate the converted amount
    conversion_rate = conversion_rates[currency1][currency2]
    converted_amount = amount_of_currency1 * conversion_rate

    return JsonResponse({'converted_amount': converted_amount})




@login_required
def send_money(request):
    sender = request.user
    sender_info = UserInfo.objects.get(user=sender)

    if request.method == "POST":
        amount = request.POST.get("amount")
        recipient_email = request.POST.get("email")

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
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
        if sender_info.balance < amount:
            messages.error(request, "Insufficient funds. Please top up your balance.")
            return render(request, 'send_money.html')

        # Check sender and recipient currencies
        valid_currencies = ["GBP", "EUR", "USD"]
        if sender_info.currency not in valid_currencies:
            raise ValidationError(f"Invalid sender currency: {sender_info.currency}")
        if recipient_currency not in valid_currencies:
            raise ValidationError(f"Invalid recipient currency: {recipient_currency}")

        converted_amount = None
        if sender_info.currency != recipient_currency:

            # Make the GET request to the conversion endpoint
            conversion_url = f"http://localhost:8000/payapp/conversion/{sender_info.currency}/{recipient_currency}/{amount}/"
            response = requests.get(conversion_url)

            if response.status_code == 200:
                data = response.json()
                converted_amount = data.get('converted_amount')
                print(f"{amount} {sender_info.currency} is equivalent to {converted_amount} {recipient_currency}")
            else:
                print(f"Conversion request failed with status code {response.status_code}")
        else:
            converted_amount = amount

        # Perform money transfer
        sender_info.balance -= Decimal(amount)
        recipient_info.balance += Decimal(converted_amount)
        sender_info.save()
        recipient_info.save()

        all_transactions = Transaction.objects.create(
            sender=sender_info,
            recipient=recipient_info,
            status="completed",
            amount=Decimal(amount),
            sender_currency=sender_info.currency
        )
        all_transactions.save()
        send_transaction_notification(sender=sender_info, recipient=recipient_info, message=f"{sender_info.user.username} sent {amount} {sender_info.currency} to {recipient_info.user.username} status: completed")

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
    send_transaction_notification(sender=recipient_user, recipient=sender_user_info, message=f"{sender_user_info.user.username} requested {amount} {sender_user_info.currency} from {recipient_user.user.username} status: pending")

    messages.success(request, f"Successfully requested {amount}  from {recipient.email}.")
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
        transaction_objs = Transaction.objects.filter(sender=receiver, recipient=sender, amount=amount).order_by('-timestamp')
        if transaction_objs.exists():
          last_transaction = transaction_objs.first()
          last_transaction.status = "completed"
          last_transaction.save()

        messages.success(request, f"Successfully accepted request from {request_obj.sender.user.username}.")
        send_transaction_notification(sender=sender, recipient=receiver, message=f"{receiver.user.username} accepted {sender.user.username} request of {amount} {sender.currency}")
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
    send_transaction_notification(sender=request_obj.receiver, recipient=request_obj.sender, message=f"{request_obj.receiver.user.username} rejected {request_obj.sender.user.username} request of {amount} {request_obj.sender.currency}")

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


def deposit(request):
    userInfo = UserInfo.objects.get(user=request.user)

    if request.method == "POST":
        amount = request.POST.get("amount_to_deposit")

        # Update the User Balance

        userInfo.balance += Decimal(amount)
        userInfo.save()
        return redirect('dashboard', pk=request.user.pk, username=request.user.username)
    return render(request, "deposit.html")