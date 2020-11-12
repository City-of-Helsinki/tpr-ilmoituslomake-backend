from django.db import models
from simple_history.models import HistoricalRecords

from base.models import Notification

# Create your models here.


class ChangeRequest(models.Model):

    target = models.ForeignKey(
        Notification, related_name="change_requests", on_delete=models.CASCADE
    )
    target_revision = models.IntegerField()

    CHANGE_TYPE_CHOICES = [
        ("change", "change"),
        ("delete", "delete"),
    ]
    change_type = models.CharField(
        max_length=16, choices=CHANGE_TYPE_CHOICES, default="change", db_index=True
    )

    # description
    description = models.TextField()
    # contact_details
    contact_details = models.TextField()

    #
    STATUS_CHOICES = [("open", "open"), ("closed", "closed")]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="open", db_index=True
    )

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


# class ModerationTask(models.Model):
#
#    #
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)
#    history = HistoricalRecords()
