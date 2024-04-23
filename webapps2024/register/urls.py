from . import views 
from django.urls import path, include


urlpatterns = [
  path("", views.home, name="home"),
  path("register/", views.register, name="register"),
  path("login/", views.signin, name="login"), 
  path('dashboard/<int:pk>/<str:username>/', views.dashboard, name='dashboard'),
  path('send_money/', views.send_money, name='send_money'),
  path('all_transactions/', views.all_transactions, name='all_transactions'),
  path('view_notifications/', views.view_notifications, name='view_notifications'),
  path('logout/', views.logout_view, name='logout'),
  path('request-money/', views.request_money, name='request_money'),
  path('pending-requests/', views.pending_requests, name='pending_requests'),
  path('accept-request/<int:pk>/', views.accept_request, name='accept_request'),  
  path('reject-request/<int:pk>/', views.reject_request, name='reject_request'),
]
