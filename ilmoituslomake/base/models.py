import json

# import uuid

from django.contrib.gis.geos import GEOSGeometry

from django.db.models import JSONField
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from users.models import User


class MatkoWord(models.Model):
    data = JSONField()


class OntologyWord(models.Model):
    data = JSONField()


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
class BaseNotification(models.Model):
    class Meta:
        abstract = True

    schema = models.IntegerField(default=1)

    # revision number
    revision = models.IntegerField(default=0, db_index=True)

    # the id of the resource in Hauki
    hauki_id = models.IntegerField(default=0)

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

    user = models.ForeignKey(
        User,
        null=True,
        related_name="%(class)s_notifications",
        on_delete=models.DO_NOTHING,
    )

    # coordinates
    location = models.PointField(srid=4326)

    # last action performed
    # action = models.CharField(max_length=16, blank=True, db_index=True)

    data = JSONField()

    # auto-fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return self.data["name"]["fi"]

    # Overwrite save
    def save(self, *args, **kwargs):
        # Auto-update revision and location
        self.revision += 1
        # leaflet is lat-lon while postgis is lon-lat
        reversed_xy = self.data["location"].copy()
        reversed_xy.reverse()
        try:
            self.location = GEOSGeometry(
                json.dumps({"type": "Point", "coordinates": reversed_xy})
            )
        except Exception as e:
            pass

        # Save notification
        super().save(*args, **kwargs)


class BaseNotificationImage(models.Model):
    class Meta:
        abstract = True

    uuid = models.UUIDField(null=True, db_index=True)

    filename = models.TextField(blank=True)

    metadata = JSONField()

    published = models.BooleanField(default=True)

    # auto-fields
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    history = HistoricalRecords(inherit=True)

    def __str__(self):
        return self.filename


class IdMappingAll(models.Model):
    palvelukartta_id = models.IntegerField(primary_key=True)
    palvelukartta_name_fi = models.TextField(null=True, blank=True)

    tpr_internal_id = models.IntegerField(null=True, blank=True)
    kaupunkialusta_id = models.IntegerField(null=True, blank=True)


class IdMappingKaupunkialustaMaster(models.Model):
    palvelukartta_id = models.IntegerField(primary_key=True)
    palvelukartta_name_fi = models.TextField(null=True, blank=True)

    tpr_internal_id = models.IntegerField(null=True, blank=True)
    kaupunkialusta_id = models.IntegerField(null=True, blank=True)


class Certificate(models.Model):
    """
    Master table for certificates and labels (merkit ja sertifikaatit).
    Contains system data for all available certificates and labels.
    """
    TYPE_CHOICES = [
        ("Label", "Label"),
        ("Certificate", "Certificate"),
    ]
    
    certificate_type = models.CharField(
        max_length=16, 
        choices=TYPE_CHOICES, 
        default="Certificate",
        db_index=True
    )
    
    # Multilingual names
    name_fi = models.CharField(max_length=125)
    name_sv = models.CharField(max_length=125)
    name_en = models.CharField(max_length=125)
    
    # URLs for more information in different languages
    url_fi = models.URLField(blank=True)
    url_sv = models.URLField(blank=True)
    url_en = models.URLField(blank=True)
    
    # Boolean flag for MyHelsinki visibility
    displayed_in_myhelsinki = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name_fi']
    
    def __str__(self):
        return f"{self.certificate_type}: {self.name_fi}"


class CustomerCertificate(models.Model):
    """
    Links customers (notifications) to certificates/labels.
    Stores the selections made in the notification form.
    """
    # Foreign key to the notification (can be Notification or ModeratedNotification)
    notification_id = models.IntegerField(db_index=True)
    
    # Foreign key to Certificate. -1 indicates "Other"
    certificate = models.ForeignKey(
        Certificate,
        on_delete=models.CASCADE,
        related_name='customer_certificates',
        null=True,
        blank=True
    )
    
    # For "Other" option - custom certificate name
    custom_name = models.CharField(max_length=255, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure uniqueness per notification and certificate
        unique_together = [['notification_id', 'certificate']]
    
    def __str__(self):
        if self.certificate:
            return f"Notification {self.notification_id} - {self.certificate.name_fi}"
        else:
            return f"Notification {self.notification_id} - Custom: {self.custom_name}"
