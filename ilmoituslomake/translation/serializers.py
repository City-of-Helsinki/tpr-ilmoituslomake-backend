from rest_framework import serializers
from moderation.serializers import ModeratedNotificationTargetSerializer
from users.serializers import ModeratorSerializer, UserSerializer
from translation.models import TranslationTask

class TranslationTaskSerializer(serializers.ModelSerializer):

    target = ModeratedNotificationTargetSerializer()
    moderator = ModeratorSerializer()

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
            "status",
            "moderator",
            "message",
            "translator",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["requestId"] = ret["request_id"]
        ret["language"] = {}
        ret["language"]["from"] = ret["language_from"]
        ret["language"]["to"] = ret["language_to"]
        ret["request"] = ret["created_at"]
        del ret["request_id"]
        del ret["language_to"]
        del ret["language_from"]

        return ret


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
            "message",
            "moderator"
        )


class TranslationRequestSerializer(serializers.ModelSerializer):
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
            "message",
            "moderator",
            "created_at",
            "updated_at"
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["language"] = {}
        ret["language"]["from"] = ret["language_from"]
        ret["language"]["to"] = ret["language_to"]
        del ret["language_to"]
        del ret["language_from"]
        del ret["target"]
        ret["request"] = ret["created_at"]
        targets = TranslationTaskSerializer(TranslationTask.objects.filter(request_id=ret["request_id"]), many=True, context={"request_id": ret["request_id"]})
        filtered_targets = []
        for item in targets.data:
            filtered_targets.append({
                "id": item["id"],
                "target": item["target"]
            })
        ret["tasks"] = filtered_targets
        ret["id"] = ret["request_id"]
        del ret["request_id"]
        return ret