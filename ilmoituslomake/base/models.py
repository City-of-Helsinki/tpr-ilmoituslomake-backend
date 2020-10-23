from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db.models import PointField
from django.db import models
from simple_history.models import HistoricalRecords


# ChangeRequest
class ChangeRequest(models.Model):

    # target id
    REQUEST_CHOICES = [
        ("change", "Change"),
        ("error", "Error"),
        ("delete", "Delete"),
    ]
    request = models.CharField(
        max_length=32,
        choices=REQUEST_CHOICES,
        default="delete",
    )
    description = models.TextField(blank=True)

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
    ]
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default="open",
    )

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


# Notification
class Notification(models.Model):

    name = models.TextField(blank=True)

    CATEGORY_CHOICES = [
        ("jokutoimiala", "Jokutoimiala"),
    ]
    category = models.CharField(
        max_length=32,
        choices=CATEGORY_CHOICES,
        default="jokutoimiala",
    )

    # notification_type
    geom = PointField()  # TODO: SRID

    # schema id & version
    data = JSONField()

    STATUS_CHOICES = [
        ("new", "New"),
        ("modified", "Modified"),
        ("approved", "Approved"),
    ]
    status = models.CharField(
        max_length=16,
        choices=STATUS_CHOICES,
        default="new",
    )

    # user
    # action

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()


# JsonSchema
class NotificationSchema(models.Model):

    name = models.TextField(blank=True)
    schema = models.TextField(blank=True)

    #
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
