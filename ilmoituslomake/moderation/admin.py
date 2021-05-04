from django.contrib import admin

# Register your models here.
# Register your models here.
from base.models import OntologyWord
from notification_form.models import Notification
from moderation.models import ModeratedNotification
from users.models import Organization


class ModeratedNotificationAdmin(admin.ModelAdmin):
    pass


class NotificationAdmin(admin.ModelAdmin):
    pass


class OntologyWordAdmin(admin.ModelAdmin):
    pass


class OrganizationAdmin(admin.ModelAdmin):
    pass


admin.site.register(ModeratedNotification, ModeratedNotificationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(OntologyWord, OntologyWordAdmin)
admin.site.register(Organization, OrganizationAdmin)
