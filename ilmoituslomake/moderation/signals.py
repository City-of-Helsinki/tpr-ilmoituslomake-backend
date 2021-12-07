from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
import requests
from ilmoituslomake.settings import HAUKI_API_URL
from opening_times.utils import update_origin

from notification_form.models import Notification
from moderation.models import ModerationItem, ModeratedNotification


@receiver(post_save, sender=Notification)
def create_moderation_item(sender, instance, **kwargs):
    # Create ModerationItem if status is not approved or rejected
    if not instance.status in ["rejected", "approved"]:
        moderated_notification = None
        try:
            if instance.moderated_notification_id > 0:
                moderated_notification = ModeratedNotification.objects.get(
                    pk=instance.moderated_notification_id
                )
        except Exception as e:
            moderated_notification = None
        moderation_item = ModerationItem(
            target=moderated_notification,
            target_revision=moderated_notification.revision
            if moderated_notification
            else 0,
            notification_target=instance,
            notification_target_revision=instance.revision,
            category="moderation_task",
            item_type=instance.status,
            data=instance.data,
        )
        moderation_item.save()

    if instance.status in ["created"]:
        try:
            update_origin(instance.id, instance.hauki_id, is_draft=True)
        except Exception as e:
            pass


@receiver(post_save, sender=ModeratedNotification)
def post_save_update_hauki_origin(sender, instance, **kwargs):
    if instance.published:
        try:
            if instance.notification_id > 0:
                notification = Notification.objects.get(pk=instance.notification_id)
                response = requests.get(
                    HAUKI_API_URL + "kaupunkialusta:" + str(instance.id) + "/"
                )
                if response.status_code != 200:
                    update_origin(instance.id, notification.hauki_id)
        except Exception as e:
            pass
