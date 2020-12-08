from rest_framework import serializers
from base.models import Notification, NotificationSchema, OntologyWord
import json
from jsonschema import validate


class OntologyWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OntologyWord
        fields = ("data",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret["data"]


# TODO: This is temp
class NotificationSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSchema
        fields = ("id", "name", "schema")


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "status", "location", "data", "updated_at", "created_at")
        read_only_fields = ("id", "status", "location", "updated_at", "created_at")

    def validate_data(self, data):
        # TODO: Improve
        schema = NotificationSchema.objects.latest("created_at").schema
        # Validate
        try:
            # Generic JSON-Schema validation
            validate(instance=data, schema=schema)
        except Exception as e:
            raise serializers.ValidationError(e)

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # TODO: Remove
        # show geometry as geojson
        ret["location"] = json.loads(instance.location.json)
        return ret
