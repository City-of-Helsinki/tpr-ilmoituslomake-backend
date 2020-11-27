from django.contrib import admin

# Register your models here.
from base.models import Notification, OntologyWord


class NotificationAdmin(admin.ModelAdmin):
    pass


class OntologyWordAdmin(admin.ModelAdmin):
    pass


admin.site.register(Notification, NotificationAdmin)
admin.site.register(OntologyWord, OntologyWordAdmin)
