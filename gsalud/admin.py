from django.contrib import admin
from gsalud.models import Users, UsersNotifications, Priorities, ReceiptTypes

admin.site.register(Users)
admin.site.register(UsersNotifications)
admin.site.register(Priorities)
admin.site.register(ReceiptTypes)
