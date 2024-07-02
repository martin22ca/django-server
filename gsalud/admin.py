from django.contrib import admin
from gsalud.models import User, UsersNotifications,  ReceiptType

admin.site.register(User)
admin.site.register(UsersNotifications)
admin.site.register(ReceiptType)