from rest_framework import serializers
from moderation.models import ModerationItem
from base.models import Notification

#
from users.serializers import ModeratorSerializer
from base.serializers import NotificationSerializer

# import json
# from jsonschema import validate


class JSONSerializerField(serializers.Field):
    # """ Serializer for JSONField -- required to make field writable"""
    def to_representation(self, obj):
        return obj["name"]["fi"]


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
        )
        read_only_fields = fields


class ChangeRequestSerializer(serializers.ModelSerializer):

    # target = serializers.IntegerField()

    class Meta:
        model = ModerationItem
        fields = ("target", "category", "item_type", "data")


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
            "user_comments",
            "user_details",
            "moderator",
            "created_at",
            "updated_at",
        )
