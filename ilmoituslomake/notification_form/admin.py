from django.contrib import admin

# Register your models here.
from base.models import Notification


class NotificationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Notification, NotificationAdmin)
