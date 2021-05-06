from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# Register your models here.
from base.models import OntologyWord
from notification_form.models import Notification
from moderation.models import ModeratedNotification, ModerationItem
from users.models import Organization


class ModeratedNotificationAdmin(SimpleHistoryAdmin):
    pass


class ModerationItemAdmin(admin.ModelAdmin):
    pass


class NotificationAdmin(SimpleHistoryAdmin):
    pass


class OntologyWordAdmin(admin.ModelAdmin):
    pass


class OrganizationAdmin(admin.ModelAdmin):
    pass


admin.site.register(ModeratedNotification, ModeratedNotificationAdmin)
admin.site.register(ModerationItem, ModerationItemAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(OntologyWord, OntologyWordAdmin)
admin.site.register(Organization, OrganizationAdmin)
