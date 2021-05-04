from rest_framework import serializers
from moderation.models import ModerationItem

# from base.models import Notification
from notification_form.models import Notification
from moderation.models import ModeratedNotification

#
from users.serializers import ModeratorSerializer
from base.serializers import NotificationSerializer

# import json
# from jsonschema import validate


class JSONSerializerField(serializers.Field):
    # """ Serializer for JSONField -- required to make field writable"""
    def to_representation(self, obj):
        return obj["name"]


class NotificationTargetSerializer(serializers.ModelSerializer):

    name = JSONSerializerField(source="data")

    class Meta:
        model = Notification
        fields = (
            "id",
            "name",
        )
        read_only_fields = fields


class ModerationItemSerializer(serializers.ModelSerializer):

    target = NotificationTargetSerializer()
    moderator = ModeratorSerializer()

    class Meta:
        model = ModerationItem
        fields = (
            "id",
            "target",
            "category",
            "item_type",
            "status",
            "moderator",
            "created_at",
            "updated_at",
            "user_place_name",
        )
        read_only_fields = fields


class ChangeRequestSerializer(serializers.ModelSerializer):

    # target = serializers.IntegerField()
    # TODO: Validate against schema
    class Meta:
        model = ModerationItem
        fields = (
            "target",
            "item_type",
            "user_place_name",
            "user_comments",
            "user_details",
        )


class ModerationItemDetailSerializer(serializers.ModelSerializer):

    target = NotificationSerializer(read_only=True)
    # data = NotificationSerializer() # Does not work because of location = GeomField
    moderator = ModeratorSerializer(read_only=True)

    class Meta:
        model = ModerationItem
        fields = (
            "id",
            "target",
            "category",
            "item_type",
            "status",
            "data",
            "user_place_name",
            "user_comments",
            "user_details",
            "moderator",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "target",
            "category",
            "item_type",
            "status",
            "user_place_name",
            "user_comments",
            "user_details",
            "moderator",
            "created_at",
            "updated_at",
        )


class PublicModeratedNotificationSerializer(serializers.ModelSerializer):

    is_notifier = serializers.SerializerMethodField()

    class Meta:
        model = ModeratedNotification
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
        # Remove some keys
        if "notifier" in ret["data"]:
            del ret["data"]["notifier"]
        # Remove created_at && user
        del ret["created_at"]
        del ret["user"]
        # show geometry as geojson
        ret["location"] = json.loads(instance.location.json)
        return ret
