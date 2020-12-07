from rest_framework import serializers
from moderation.models import ModerationItem
from base.models import Notification

#
from users.serializers import ModeratorSerializer

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


class ModerationItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationItem
        fields = (
            "id",
            "target",
            "target_revision",
            "category",
            "item_type",
            "status",
            "data",
            "user_comments",
            "user_details",
            "moderator_comments",
            "moderator",
            "created_at",
            "updated_at",
        )
        read_only_fields = "id"
