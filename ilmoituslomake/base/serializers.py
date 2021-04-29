from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

# from ilmoituslomake.settings import AZURE_READ_KEY

from base.models import (
    Notification,
    NotificationSchema,
    OntologyWord,
    NotificationImage,
)
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


class NotificationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationImage
        fields = ("metadata",)
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["metadata"]["url"] = (
            instance.data.url
            + "?sv=2019-12-12&ss=bf&srt=sco&sp=r&se=2021-03-31T13:17:17Z&st=2021-02-14T06:17:17Z&spr=https&sig=XcDH%2F6NT26aRx5K2NRqrzVxo7AwoLuM2TNXRyvK%2F9Iw%3D"
        )  # TODO: Move this to ModerationSerializer
        return ret["metadata"]


class NotificationSerializer(serializers.ModelSerializer):

    is_notifier = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "status",
            "is_notifier",
            "user",
            #            "location",
            "data",
            "updated_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "status",
            "is_notifier",
            "user",
            #            "location",
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

    def get_is_notifier(self, obj):
        if obj.user == None:
            return False

        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        if obj.user == user:
            return True

        return False

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Check if user is notifier, and only return notifier details if so
        is_notifier = self.get_is_notifier(instance)
        # Remove some keys, but always return notifier_type
        if is_notifier is False and "notifier" in ret["data"]:
            if "full_name" in ret["data"]["notifier"]:
                del ret["data"]["notifier"]["full_name"]
            if "email" in ret["data"]["notifier"]:
                del ret["data"]["notifier"]["email"]
            if "phone" in ret["data"]["notifier"]:
                del ret["data"]["notifier"]["phone"]
        # Remove created_at && user
        del ret["data"]["images"]
        del ret["created_at"]
        del ret["user"]
        # show geometry as geojson
        # ret["location"] = json.loads(instance.location.json)
        # images
        serializer = NotificationImageSerializer(instance.images, many=True)
        ret["data"]["images"] = serializer.data
        return ret
