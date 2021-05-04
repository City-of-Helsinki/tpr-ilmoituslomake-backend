from django.contrib.gis.db import models
from base.models import BaseNotification, BaseNotificationImage
from users.models import Organization

# Create your models here.
class Notification(BaseNotification):

    organization = models.ForeignKey(
        Organization,
        null=True,
        related_name="organization_notifications",
        on_delete=models.DO_NOTHING,
    )


class NotificationImage(BaseNotificationImage):
    notification = models.ForeignKey(
        Notification, null=True, related_name="images", on_delete=models.DO_NOTHING
    )
