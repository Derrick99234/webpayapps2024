from . import views 
from django.urls import path

urlpatterns = [
    path('dashboard/<int:pk>/<str:username>/', views.dashboard, name='dashboard'),
    path('send_money/', views.send_money, name='send_money'),
    path('all_transactions/', views.all_transactions, name='all_transactions'),
    path('view_notifications/', views.view_notifications, name='view_notifications'),
    path('conversion/<str:currency1>/<str:currency2>/<amount_of_currency1>/', views.convert_currency, name='conversion'),
    path('request-money/', views.request_money, name='request_money'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('accept-request/<int:pk>/', views.accept_request, name='accept_request'), 
    path('reject-request/<int:pk>/', views.reject_request, name='reject_request'),
    path('logout/', views.logout_view, name='logout'),
    path('deposit/', views.deposit, name='deposit'),
]
