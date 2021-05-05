import json
from jsonschema import validate

from rest_framework import serializers

from base.models import NotificationSchema
from notification_form.models import Notification, NotificationImage


class NotificationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationImage
        fields = ("metadata",)
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["metadata"]["url"] = instance.data.url.replace(
            "tprimages.blob.core.windows.net/", "/"
        )
        return ret["metadata"]
