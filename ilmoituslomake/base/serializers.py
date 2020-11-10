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
        fields = ("id", "data")

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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # TODO: Remove
        # show geometry as geojson
        # ret["location"] = json.loads(instance.location.json)
        return ret
