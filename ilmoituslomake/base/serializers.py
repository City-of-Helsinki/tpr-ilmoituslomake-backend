from rest_framework import serializers
from base.models import Notification, NotificationSchema
from django.contrib.gis.db.models.functions import AsGeoJSON

# from django.contrib.gis.geos import GEOSGeometry
from jsonschema import validate


# TODO: This is temp
class NotificationSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSchema
        fields = ("id", "name", "schema")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "location", "data")

    def validate_data(self, data):
        # TODO: Improve
        schema = NotificationSchema.objects.get(pk=1).schema
        # Validate
        try:
            # Generic JSON-Schema validation
            validate(instance=data, schema=schema)
        except Exception as e:
            raise serializers.ValidationError(e)

        return data
