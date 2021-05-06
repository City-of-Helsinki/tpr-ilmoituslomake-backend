from django.db.models.signals import post_save
from django.dispatch import receiver

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
            category="moderation_task",
            item_type=instance.status,
            data=instance.data,
        )
        moderation_item.save()
