from django.db import models
from moderation.models import ModeratedNotification
from simple_history.models import HistoricalRecords

from users.models import User

class TranslationTask(models.Model):

    requestId = models.IntegerField()
    
    target = models.ForeignKey(
        ModeratedNotification,
        null=True,
        related_name="translation_items",
        on_delete=models.CASCADE,
    )

    CATEGORY_CHOICES = [
        ("change_request", "change_request"),
        ("translation_edit", "translation_edit"),
        ("translation_task", "translation_task"),
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

    STATUS_CHOICES = [
        ("open", "open"),
        ("in_progress", "in_progress"),
        ("closed", "closed"),
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="open", db_index=True
    )

    # data = models.JSONField()

    translator = models.ForeignKey(
        User, null=True, related_name="translation_translator", on_delete=models.DO_NOTHING
    )

    moderator = models.ForeignKey(
        User, null=True, related_name="translation_moderator", on_delete=models.DO_NOTHING
    )

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()