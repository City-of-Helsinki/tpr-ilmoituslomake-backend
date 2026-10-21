from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from base.models import OntologyWord
from notification_form.models import Notification, NotificationImage
from moderation.models import ModeratedNotification, ModerationItem
from users.models import Organization


@admin.register(ModeratedNotification)
class ModeratedNotificationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(ModerationItem)
class ModerationItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Notification)
class NotificationAdmin(SimpleHistoryAdmin):
    pass


@admin.register(NotificationImage)
class NotificationImageAdmin(SimpleHistoryAdmin):
    pass


@admin.register(OntologyWord)
class OntologyWordAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


