from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserInfo
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.exceptions import ValidationError  # For currency validation
# from django.core.serializers.json import DjangoJSONEncoder
# import json
# Create your views here.

def home(request):
    return render(request, 'index.html')

def signin(request):
    if request.method == "POST":
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        # Check if the username_or_email contains "@" symbol
        if '@' in username_or_email:
            user = authenticate(request, email=username_or_email, password=password)
        else:
            user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)

            messages.success(request, "Login successful.")
            return redirect('dashboard', username=user.username)
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
        
        UserInfo.objects.create(
            first_name = fname,
            last_name = lname,
            username = username,
            currency = currency,
            balance = initial_amount,
            email = email,
        )
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()

        messages.success(request, "Account created successfully. You can now login.")

        return redirect('login')

    return render(request, 'authentication/register.html')

class SendMoneyForm(forms.Form):
    amount = forms.FloatField(min_value=0.01, required=True)  # Validate amount (positive)
    email = forms.EmailField(required=True)

def dashboard(request, username):
    userInfo = UserInfo.objects.get(username=username)
    context = {
            "username" : userInfo.username,
            "balance" : userInfo.balance,
            "currency" : userInfo.currency,
            "currency" : userInfo.currency,
        }
    return render(request, "dashboard.html", context)

def convert_currency(amount, from_currency, to_currency):
    conversion_rates = {
         "GBP": {"USD": 1.30, "EUR": 1.15},  # Example rates for GBP
        "EUR": {"USD": 1.10, "GBP": 0.87},  # Example rates for EUR
        "USD": {"EUR": 0.91, "GBP": 0.77},  # Example rates for USD
    }
    converted_amount = amount * conversion_rates[from_currency][to_currency]
    return converted_amount


@login_required
def send_money(request):
    if request.method == "POST":
        amount = request.POST["amount"]
        recipient_email = request.POST["email"]

        # Validate user input (e.g., ensure amount is positive)
        if not amount.isdigit() or float(amount) <= 0:
            messages.error(request, "Invalid amount. Please enter a positive number.")
            return render(request, 'send_money.html')

        # Retrieve recipient user object based on email (assuming a verified user list)
        try:
            recipient = User.objects.get(email=recipient_email)
            recipient_info = UserInfo.objects.get(username=recipient)  # Get recipient's UserInfo
            recipient_currency = recipient_info.currency
        except User.DoesNotExist:
            messages.error(request, "Recipient with this email address not found.")
            return render(request, 'send_money.html')

        # Get sender's UserInfo object (assuming user is linked to UserInfo)
        sender_info = UserInfo.objects.get(username=request.user)

        # Check sender's account balance
        if sender_info.balance < float(amount):
            messages.error(request, "Insufficient funds. Please top up your balance.")
            return render(request, 'send_money.html')

        # Currency Validation
        valid_currencies = ["GBP", "EUR", "USD"]  # Replace with your allowed currencies

        if sender_info.currency not in valid_currencies:
            raise ValidationError(f"Invalid sender currency: {sender_info.currency}")
        if recipient_currency and recipient_currency not in valid_currencies:
            raise ValidationError(f"Invalid recipient currency: {recipient_currency}")

        # Handle Currency Conversion (Optional)
        if sender_info.currency != recipient_currency and recipient_currency:
            # Implement currency conversion logic here (e.g., using an external API)
            # Ensure you handle potential conversion errors or unavailable rates
            converted_amount = convert_currency(float(amount), sender_info.currency, recipient_currency)
            # Update 'amount' variable with the converted amount for further processing
            amount = converted_amount

        # Implement secure transaction processing logic here (e.g., call a payment gateway API)
        # This part will depend on your chosen transaction processing method

        # Upon successful transaction, update sender and recipient balances
        sender_info.balance -= float(amount)
        recipient_info.balance += float(amount)
        sender_info.save()  # Save changes to sender's balance
        recipient_info.save()  # Save changes to recipient's balance

        messages.success(request, f"Successfully sent {amount} {sender_info.currency} to {recipient.email}.")
        return redirect('dashboard', username=request.user)

    # Optional: Allow specifying recipient currency in the form
    return render(request, 'send_money.html', {'valid_currencies': valid_currencies})
