from django.contrib import admin
from .models import Users,UsersRoles,UsersNotifications,Priorities,ReceiptTypes

admin.site.register(Users)
admin.site.register(UsersRoles)
admin.site.register(UsersNotifications)
admin.site.register(Priorities)
admin.site.register(ReceiptTypes)