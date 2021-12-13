from rest_framework import serializers
from moderation.models import ModerationItem

from base.models import NotificationSchema
from notification_form.models import Notification, NotificationImage
from moderation.models import ModeratedNotification, ModeratedNotificationImage

#
from users.serializers import ModeratorSerializer, UserSerializer

# from base.serializers import NotificationSerializer
from notification_form.serializers import (
    NotificationImageSerializer,
)

from ilmoituslomake.settings import PUBLIC_AZURE_CONTAINER

import json
from jsonschema import validate


class ModeratedNotificationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeratedNotificationImage
        fields = ("metadata",)
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        id = self.context.get("id", None)
        image_metadata = self.context.get("images")[ret["metadata"]["uuid"]]
        if id != None:
            image = ret["metadata"]["uuid"] + ".jpg"
            ret["metadata"] = image_metadata
            ret["metadata"]["url"] = (
                "https://tprimages.blob.core.windows.net/"
                + PUBLIC_AZURE_CONTAINER
                + "/"
                + str(id)
                + "/"
                + image
            )
        return ret["metadata"]


class JSONSerializerField(serializers.Field):
    # """ Serializer for JSONField -- required to make field writable"""
    def to_representation(self, obj):
        return obj["name"]


class ModeratedNotificationTargetSerializer(serializers.ModelSerializer):

    name = JSONSerializerField(source="data")

    class Meta:
        model = ModeratedNotification
        fields = (
            "id",
            "name",
        )
        read_only_fields = fields


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

    target = ModeratedNotificationTargetSerializer()
    notification_target = NotificationTargetSerializer()
    moderator = ModeratorSerializer()

    class Meta:
        model = ModerationItem
        fields = (
            "id",
            "target",
            "notification_target",
            "category",
            "item_type",
            "status",
            "moderator",
            "created_at",
            "updated_at",
            "user_place_name",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret["target"] != None and instance.target.status == "rejected":

            ret["status"] = "rejected"
        return ret


class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationItem
        fields = (
            "id",
            "target",
            "category",
            "item_type",
            "user_place_name",
            "user_comments",
            "user_details",
        )


class ApproveModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("data",)
        read_only_fields = ("data",)

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


class ModerationNotificationSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id",
            "status",
            "user",
            "location",
            "data",
            # "moderated_notification_id",
            "updated_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "status",
            "user",
            "location",
            # "moderated_notification_id",
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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Show geometry as geojson
        ret["location"] = json.loads(instance.location.json)
        # images
        serializer = NotificationImageSerializer(
            NotificationImage.objects.all().filter(
                notification=instance.pk,
                # published=True,
                uuid__in=list(map(lambda i: i["uuid"], ret["data"]["images"])),
            ),
            many=True,
            context={
                "id": instance.pk,
                "images": {image["uuid"]: image for image in ret["data"]["images"]},
            },
        )  # TODO
        ret["data"]["images"] = serializer.data
        return ret


class PrivateModeratedNotificationSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta:
        model = ModeratedNotification
        fields = (
            "id",
            "published",
            "user",
            "location",
            "data",
            "updated_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "published",
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

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Show geometry as geojson
        ret["location"] = json.loads(instance.location.json)
        # images
        serializer = ModeratedNotificationImageSerializer(
            ModeratedNotificationImage.objects.all().filter(
                notification=instance.pk,
                published=True,
                uuid__in=list(map(lambda i: i["uuid"], ret["data"]["images"])),
            ),
            many=True,
            context={
                "id": instance.pk,
                "images": {image["uuid"]: image for image in ret["data"]["images"]},
            },
        )  # TODO
        ret["data"]["images"] = serializer.data
        return ret


class ModerationItemDetailSerializer(serializers.ModelSerializer):

    notification_target = ModerationNotificationSerializer(read_only=True)
    target = PrivateModeratedNotificationSerializer(read_only=True)
    # data = NotificationSerializer() # Does not work because of location = GeomField
    moderator = ModeratorSerializer(read_only=True)

    class Meta:
        model = ModerationItem
        fields = (
            "id",
            "notification_target",
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
            "notification_target",
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
            "is_notifier",
            "published",
            "user",
            "location",
            "data",
            "updated_at",
            "created_at",
        )
        read_only_fields = (
            "id",
            "is_notifier",
            "published",
            "user",
            "location",
            "data",
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
        if "notifier" in ret["data"] and not is_notifier:
            del ret["data"]["notifier"]["full_name"]
            del ret["data"]["notifier"]["email"]
            del ret["data"]["notifier"]["phone"]
        # Remove created_at && user
        del ret["created_at"]
        del ret["user"]
        # show geometry as geojson
        ret["location"] = json.loads(instance.location.json)
        # images
        # instance.images
        serializer = ModeratedNotificationImageSerializer(
            ModeratedNotificationImage.objects.all().filter(
                notification=instance.pk,
                published=True,
                uuid__in=list(map(lambda i: i["uuid"], ret["data"]["images"])),
            ),
            many=True,
            context={
                "id": instance.pk,
                "images": {image["uuid"]: image for image in ret["data"]["images"]},
            },
        )
        del ret["data"]["images"]
        ret["data"]["images"] = serializer.data
        return ret
