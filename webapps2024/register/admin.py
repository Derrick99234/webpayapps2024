from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(UserInfo)
admin.site.register(Request)
admin.site.register(Transaction)
admin.site.register(Notification)