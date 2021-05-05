from django.contrib.gis.db import models
from base.models import BaseNotification, BaseNotificationImage

# from moderation.models import ModeratedNotification
from users.models import Organization

# Create your models here.
class Notification(BaseNotification):

    organization = models.ForeignKey(
        Organization,
        null=True,
        related_name="organization_notifications",
        on_delete=models.DO_NOTHING,
    )

    #
    moderated_notification_id = models.IntegerField(default=0)


class NotificationImage(BaseNotificationImage):
    notification = models.ForeignKey(
        Notification, null=True, related_name="images", on_delete=models.DO_NOTHING
    )
