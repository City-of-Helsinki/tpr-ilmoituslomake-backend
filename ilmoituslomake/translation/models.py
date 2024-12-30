from typing import Dict
from django.db import models
from moderation.models import ModeratedNotification
from simple_history.models import HistoricalRecords
from django.db.models import JSONField

from users.models import User

class TranslationTask(models.Model):
    
    published = models.BooleanField(default=False, db_index=True)

    request_id = models.IntegerField()
    
    target = models.ForeignKey(
        ModeratedNotification,
        null=True,
        related_name="translation_items",
        on_delete=models.CASCADE,
    )
    target_revision = models.IntegerField(default=0, db_index=True)

    language_from = models.TextField()
    language_to = models.TextField()

    CATEGORY_CHOICES = [
        ("translation_task", "translation_task"),
    ]

    category = models.CharField(
        max_length=16, choices=CATEGORY_CHOICES, default="translation_task", db_index=True
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
        max_length=16, choices=ITEM_TYPE_CHOICES, default="created", db_index=True
    )

    STATUS_CHOICES = [
        ("open", "open"),
        ("in_progress", "in_progress"),
        ("closed", "closed"),
        ("cancelled", "cancelled"),
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="open", db_index=True
    )

    data = JSONField(default=dict)

    message = models.TextField()

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


class TranslationData(models.Model):
    
    task_id = models.ForeignKey(
        TranslationTask,
        null=True,
        related_name="translation_items",
        on_delete=models.CASCADE,
    )

    target_revision = models.IntegerField()
    language = models.TextField()
    name = models.TextField()
    description_long = models.TextField()
    description_short = models.TextField()
    images = JSONField(default=dict)
    website = models.TextField()
