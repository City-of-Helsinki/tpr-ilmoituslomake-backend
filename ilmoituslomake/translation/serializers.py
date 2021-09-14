from rest_framework import serializers
from moderation.serializers import PrivateModeratedNotificationSerializer, ModeratedNotificationTargetSerializer
from users.serializers import ModeratorSerializer, TranslatorSerializer, UserSerializer
from translation.models import TranslationData, TranslationTask
from django.forms.models import model_to_dict
class TranslationTaskSerializer(serializers.ModelSerializer):

    target = ModeratedNotificationTargetSerializer()
    moderator = ModeratorSerializer()
    # translator = TranslatorSerializer

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


class TranslationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationData
        fields = (
            "task_id",
            "language",
            "name",
            "description_long",
            "description_short",
            "images",
            "website"
        )
        read_only_fields = fields
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)

        name_temp = ret["name"]
        del ret["name"]
        ret["name"] = {}
        ret["name"]["lang"] = name_temp

        ret["description"] = {}
        ret["description"]["short"] = {}
        ret["description"]["long"] = {}
        ret["description"]["short"]["lang"] = ret["description_short"]
        ret["description"]["long"]["lang"] = ret["description_short"]
        del ret["description_short"]
        del ret["description_long"]

        website_temp = ret["website"]
        del ret["website"]
        ret["website"] = {}
        ret["website"]["lang"] = website_temp

        del ret["task_id"]
        # TODO: Add rest of the data
        return ret


class TranslationTaskWithDataSerializer(serializers.ModelSerializer):

    target = PrivateModeratedNotificationSerializer()
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
        data = TranslationDataSerializer(
            TranslationData.objects.filter(task_id=ret["id"]), 
            many=True, context={"task_id": ret["id"]}
        )        
        if data.data == []:
            tasks_with_same_target = TranslationTask.objects.filter(target=ret["target"]["id"])
            data_with_same_target = []
            for task in tasks_with_same_target:
                if task.published:
                    data_with_task_id = TranslationData.objects.filter(task_id=task.id)
                    if data_with_task_id:
                        data_with_same_target.extend(data_with_task_id)

            if len(data_with_same_target) != 0:
                newest_data = max(data_with_task_id, key=lambda x:x.task_id)
                data_serializer = TranslationDataSerializer(newest_data)
                ret["data"] = data_serializer.data
            else:
                ret["data"] = {}
        else:   
            ret["data"] = data.data[0]

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
        targets = TranslationTaskSerializer(
            TranslationTask.objects.filter(request_id=ret["request_id"]), 
            many=True, context={"request_id": ret["request_id"]}
        )
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