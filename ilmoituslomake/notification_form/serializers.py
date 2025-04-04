import json
import jwt
import datetime

from jsonschema import validate

from rest_framework import serializers

from base.models import NotificationSchema
from notification_form.models import Notification, NotificationImage


from ilmoituslomake.settings import JWT_IMAGE_SECRET, FULL_WEB_ADDRESS

# TODO: Create settings variable that contains localhost/api per domain


class NotificationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationImage
        fields = ("metadata",)
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        id = self.context.get("id", None)
        image_metadata = self.context.get("images")[ret["metadata"]["uuid"]]
        if id != None:
            image = ret["metadata"]["uuid"] + ".jpg"
            ret["metadata"] = image_metadata
            token = jwt.encode(
                {
                    "id": str(id),
                    "image": image,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=180),
                },
                JWT_IMAGE_SECRET,
                algorithm="HS256",
            )
            ret["metadata"]["url"] = (
                FULL_WEB_ADDRESS
                + "/api/proxy/"
                + str(id)
                + "/"
                + image
                + "?token="
                # + token.decode("utf-8") # python 2
                + token # python 3
            )
        return ret["metadata"]
