from django.contrib.gis.db import models
from django.shortcuts import get_object_or_404

from simple_history.models import HistoricalRecords
from django.contrib.postgres.fields import JSONField

from base.models import BaseNotification, BaseNotificationImage
from notification_form.models import Notification

from users.models import User

from moderation.storage import PublicAzureStorage

afs = PublicAzureStorage()

# Create your models here.


class ModeratedNotification(BaseNotification):
    # is published
    published = models.BooleanField(default=False, db_index=True)

    #
    notification_id = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.hauki_id == 0:
            try:
                if self.notification_id != 0:
                    notification = Notification.objects.get(pk=self.notification_id)
                    self.hauki_id = notification.hauki_id
                    # TODO: Update name etc. in hauki????
            except Exception as e:
                pass
        return super().save(*args, **kwargs)

    # works for fi, sv and end
    def has_lang(self, lang):
        if "name" in self.data and lang in self.data["name"]:
            return self.data["name"][lang] != ""
        return False


def upload_image_to(instance, filename):
    #     return "{0}/{1}".format("1", filename)
    return "{0}/{1}".format(instance.notification.pk, filename)


class ModeratedNotificationImage(BaseNotificationImage):

    data = models.ImageField(storage=afs, upload_to=upload_image_to)

    notification = models.ForeignKey(
        ModeratedNotification,
        null=True,
        related_name="images",
        on_delete=models.DO_NOTHING,
    )


class ModerationItem(models.Model):

    notification_target = models.ForeignKey(
        Notification,
        null=True,
        related_name="moderation_items",
        on_delete=models.CASCADE,
    )
    notification_target_revision = models.IntegerField(default=0)

    target = models.ForeignKey(
        ModeratedNotification,
        null=True,
        related_name="moderation_items",
        on_delete=models.CASCADE,
    )
    target_revision = models.IntegerField(default=0)

    CATEGORY_CHOICES = [
        ("change_request", "change_request"),
        ("moderator_edit", "moderator_edit"),
        ("moderation_task", "moderation_task"),
    ]
    category = models.CharField(
        max_length=16, choices=CATEGORY_CHOICES, default="change_request", db_index=True
    )

    CHANGE_TYPE_CHOICES = [
        ("change", "change"),
        ("add", "add"),
        ("delete", "delete"),
    ]
    MODERATION_TYPE_CHOICES = [
        ("created", "created"),
        ("modified", "modified"),
    ]
    ITEM_TYPE_CHOICES = CHANGE_TYPE_CHOICES + MODERATION_TYPE_CHOICES
    item_type = models.CharField(
        max_length=16, choices=ITEM_TYPE_CHOICES, default="change", db_index=True
    )

    #
    STATUS_CHOICES = [
        ("open", "open"),
        ("in_progress", "in_progress"),
        ("closed", "closed"),
        ("rejected", "rejected"),
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="open", db_index=True
    )

    #
    data = JSONField(default=dict)

    #
    user_place_name = models.TextField(default="", blank=True)
    user_comments = models.TextField(default="")
    user_details = models.TextField(default="", blank=True)

    # moderator_comments = models.TextField(default="")
    moderator = models.ForeignKey(
        User, null=True, related_name="tasks", on_delete=models.DO_NOTHING
    )

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def is_completed(self):
        return self.status == "closed" or self.status == "rejected"
