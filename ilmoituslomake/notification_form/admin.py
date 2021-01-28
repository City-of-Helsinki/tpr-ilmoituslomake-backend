from django.contrib import admin

# Register your models here.
from base.models import Notification, OntologyWord, Image


class NotificationAdmin(admin.ModelAdmin):
    pass


class OntologyWordAdmin(admin.ModelAdmin):
    pass


class ImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Notification, NotificationAdmin)
admin.site.register(OntologyWord, OntologyWordAdmin)

admin.site.register(Image, ImageAdmin)
