from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from users.models import User


# Notification
class Notification(models.Model):

    # revision number
    revision = models.IntegerField(default=0)

    # notification status
    STATUS_CHOICES = [
        ("created", "created"),
        ("modified", "modified"),
        ("approved", "approved"),
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="created", db_index=True
    )

    # is published - only approved & published items are show in API
    published = models.BooleanField(default=False, db_index=True)

    # last action performed
    action = models.CharField(max_length=16, blank=True)
    location = models.PointField(srid=4326)

    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    reporter = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    comments = models.TextField(blank=True)

    schema = models.ForeignKey(NotificationSchema, on_delete=models.DO_NOTHING)
    schema_revision = models.IntegerField()
    data = JSONField()

    #
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    history = HistoricalRecords()


# JsonSchema
class NotificationSchema(models.Model):

    # revision number
    revision = models.IntegerField(default=0)

    # description of the schema
    name = models.TextField(blank=True)
    schema = JSONField()

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


# ChangeRequest
# class ChangeRequest(models.Model):
#
#    # target id
#    REQUEST_CHOICES = [
#        ("change", "Change"),
#        ("error", "Error"),
#        ("delete", "Delete"),
#    ]
#    request = models.CharField(
#        max_length=32,
#        choices=REQUEST_CHOICES,
#        default="delete",
#    )
#    description = models.TextField(blank=True)
#
#    STATUS_CHOICES = [
#        ("open", "Open"),
#        ("closed", "Closed"),
#    ]
#    status = models.CharField(
#        max_length=16,
#        choices=STATUS_CHOICES,
#        default="open",
#    )
#
#    #
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)
#    history = HistoricalRecords()
