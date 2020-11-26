from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from django.contrib.postgres.fields import JSONField

from base.models import Notification

from users.models import User

# Create your models here.


class ModerationItem(models.Model):

    target = models.ForeignKey(
        Notification, related_name="moderation_tasks", on_delete=models.CASCADE
    )
    target_revision = models.IntegerField()

    CATEGORY_CHOICES = [
        ("change_request", "change_request"),
        ("moderation_task", "moderation_task"),
    ]
    category = models.CharField(
        max_length=16, choices=CATEGORY_CHOICES, default="change_request", db_index=True
    )

    CHANGE_TYPE_CHOICES = [
        ("change", "change"),
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
        ("new", "new"),
        ("open", "open"),
        ("in_progress", "in_progress"),
        ("closed", "closed"),
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="new", db_index=True
    )

    #
    data = JSONField()

    #
    user_comments = models.TextField(default="")
    user_details = models.TextField(default="")

    # moderator_comments = models.TextField(default="")
    # moderator =

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
