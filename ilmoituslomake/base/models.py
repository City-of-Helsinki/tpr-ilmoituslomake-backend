import json
import uuid

from django.contrib.gis.geos import GEOSGeometry

from django.contrib.postgres.fields import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from users.models import User

from base.storage import PublicAzureStorage

afs = PublicAzureStorage()


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
    # published = models.BooleanField(default=False, db_index=True)

    user = models.ForeignKey(
        User, null=True, related_name="notifications", on_delete=models.DO_NOTHING
    )

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


def upload_image_to(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "{0}/{1}".format(instance.notification.pk, str(uuid.uuid4()))


class Image(models.Model):

    name = models.TextField(blank=True)
    filename = models.TextField(blank=True)

    photo = models.ImageField(storage=afs, upload_to=upload_image_to)

    notification = models.ForeignKey(
        Notification, related_name="photos", on_delete=models.DO_NOTHING
    )

    # auto-fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.photo.url
