from . import views 
from django.urls import path, include


urlpatterns = [
  path("", views.home, name="home"),
  path("register/", views.register, name="register"),
  path("login/", views.signin, name="login"),
  path('dashboard/<str:username>/', views.dashboard, name='dashboard'),
  path('send_money/', views.send_money, name='send_money'),
]
