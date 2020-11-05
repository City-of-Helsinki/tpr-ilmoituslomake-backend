from rest_framework import serializers
from base.models import Notification


class ToimipisterekisteriNotificationAPISerializer(serializers.ModelSerializer):
    """
    Serializes Notification Model for Toimipisterekisteri API
    """

    class Meta:
        model = Notification
        fields = ("id", "published", "location", "data", "updated_at", "created_at")

    # def to_representation(self, instance):
    #     notif = super().to_representation(instance)

    #     # Location as coordinates [12,34]
    #     notif["location"] = instance.location.coordinates

    #     # Merge data property to root and delete it afterwards
    #     notif.update(notif["data"])
    #     del notif["data"]

    #     return notif
