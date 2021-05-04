from django.contrib import admin

# Register your models here.
from base.models import OntologyWord
from notification_form.models import Notification
from moderation.models import ModeratedNotification


class ModeratedNotificationAdmin(admin.ModelAdmin):
    pass


class NotificationAdmin(admin.ModelAdmin):
    pass


class OntologyWordAdmin(admin.ModelAdmin):
    pass


admin.site.register(ModeratedNotification, ModeratedNotificationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(OntologyWord, OntologyWordAdmin)
