import json

from django.contrib.gis.geos import GEOSGeometry

from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from users.models import User


class OntologyWord(models.Model):
    data = JSONField()

    # def __str__(self):
    #    return self.data['ontologyword']['fi']


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


# Notification
class Notification(models.Model):

    # revision number
    revision = models.IntegerField(default=0, db_index=True)

    # notification status
    STATUS_CHOICES = [
        ("created", "created"),
        ("modified", "modified"),
        ("rejected", "rejected"),
        ("approved", "approved"),
    ]
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default="created", db_index=True
    )

    # is published
    published = models.BooleanField(default=False, db_index=True)

    # coordinates
    location = models.PointField(srid=4326)

    # last action performed
    # action = models.CharField(max_length=16, blank=True, db_index=True)

    data = JSONField()

    # auto-fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.data["name"]["fi"]

    # Overwrite save
    def save(self, *args, **kwargs):
        # Auto-update location
        # TODO: Handle error
        self.revision += 1
        self.location = GEOSGeometry(
            json.dumps({"type": "Point", "coordinates": self.data["location"]})
        )
        # Save notification
        super().save(*args, **kwargs)
