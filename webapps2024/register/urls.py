from . import views 
from django.urls import path, include


urlpatterns = [
  path("", views.home, name="home"),
  path("register/", views.register, name="register"),
  path("login/", views.signin, name="login"), 
  path("payapp/", include('payapp.urls')), 

]
