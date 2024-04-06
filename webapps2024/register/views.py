from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login

# Create your views here.

def home(request):
    return render(request, 'index.html')

def signin(request):
     if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('passwords')

        user = authenticate(username=username, email=email, password=password)

        if user is not None:
            login(request, user)
            username = user.username
            return render(request, 'authentication/dashboard.html', {"username": username})
        else:
            messages.error(request, "Login credentials not correct")
            return redirect('login')
     
     return render(request, 'authentication/login.html')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']


        myuser = User.objects.create_user(username, email, password1)
        myuser.save()

        messages.success(request, "Account Created Successfully")
        return redirect('login')




    return render(request, 'authentication/register.html')

