from rest_framework import serializers
from moderation.models import ModerationItem

import json
from jsonschema import validate


class ModerationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationItem
        fields = (
            "target",
            "category",
            "item_type",
            "status",
            "created_at",
            "updated_at",
        )


class ModerationItemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationItem
        fields = (
            "target",
            "target_revision",
            "category",
            "item_type",
            "status",
            "data",
            "user_comments",
            "user_details",
            "moderator_comments",
            "created_at",
            "updated_at",
        )
