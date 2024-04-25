from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import UserInfo
from django import forms
from django.contrib.auth import logout
# from django.dispatch import receiver
# from django.contrib.auth.signals import user_logged_in    
# from django.core.serializers.json import DjangoJSONEncoder
# Create your views here.
def home(request):
    return render(request, 'index.html')

# def send_transaction_notification(sender, recipient, message):
#     Notification.objects.create(user=sender, message=message)
#     Notification.objects.create(user=recipient, message=message)

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
