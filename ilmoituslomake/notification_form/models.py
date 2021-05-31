from django.contrib.gis.db import models
from base.models import BaseNotification, BaseNotificationImage

# from moderation.models import ModeratedNotification
from users.models import Organization

from notification_form.storage import PrivateAzureStorage

afs = PrivateAzureStorage()

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

    # # Overwrite save
    # def notification_save(self, ):

    #     # Process images
    #     try:
    #         pass
    #     except Exception as e:
    #         pass
    #     # Save notification
    #     return self.save()


def upload_image_to(instance, filename):
    #     return "{0}/{1}".format("1", filename)
    return "{0}/{1}".format(instance.notification.pk, filename)


class NotificationImage(BaseNotificationImage):

    data = models.ImageField(storage=afs, upload_to=upload_image_to)

    notification = models.ForeignKey(
        Notification, null=True, related_name="images", on_delete=models.DO_NOTHING
    )
