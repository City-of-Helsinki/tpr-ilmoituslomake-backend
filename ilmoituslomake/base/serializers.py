from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from base.models import NotificationSchema, OntologyWord
from notification_form.models import Notification
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

    # is_notifier = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "status",
            "is_notifier",
            "user",
            "location",
            "data",
            "updated_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "status",
            "is_notifier",
            "user",
            "location",
            "updated_at",
            "created_at",
        )

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

    # def get_is_notifier(self, obj):
    #     if obj.user == None:
    #         return False

    #     user = None
    #     request = self.context.get("request")
    #     if request and hasattr(request, "user"):
    #         user = request.user

    #     if obj.user == user:
    #         return True

    #     return False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Remove some keys
        if "notifier" in ret["data"]:
            del ret["data"]["notifier"]
        # Remove created_at && user
        del ret["created_at"]
        del ret["user"]
        # show geometry as geojson
        ret["location"] = json.loads(instance.location.json)
        return ret
