from rest_framework import serializers
from moderation.serializers import ModeratedNotificationTargetSerializer
from users.serializers import ModeratorSerializer, UserSerializer
from translation.models import TranslationTask

class TranslationTaskSerializer(serializers.ModelSerializer):

    target = ModeratedNotificationTargetSerializer()
    moderator = ModeratorSerializer()
    translator = UserSerializer()

    class Meta:
        model = TranslationTask
        fields = (
            "id",
            "request_id"
            "target",
            "language_from",
            "language_to",
            "category",
            "item_type",
            "status",
            "moderator",
            "translator",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationTask
        fields = (
            "id",
            "request_id",
            "target",
            "language_from",
            "language_to",
            "category",
            "item_type",
            "translator",
        )