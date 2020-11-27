from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import Notification
from moderation.models import ModerationItem


@receiver(post_save, sender=Notification)
def create_moderation_item(sender, instance, **kwargs):
    # Create ModerationItem if status is not approved or rejected
    if not instance.status in ["rejected", "approved"]:
        moderation_item = ModerationItem(
            target=instance,
            target_revision=instance.revision,
            category="moderation_task",
            item_type=instance.status,
            data=instance.data,
        )
        moderation_item.save()
