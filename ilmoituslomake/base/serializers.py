from rest_framework import serializers
from base.models import Notification
from django.contrib.gis.db.models.functions import AsGeoJSON


class NotificationSerializer(serializers.Serializer):
    class Meta:
        model = Notification
        fields = ("id", "name", "geom", "data")
        # read_only_fields = ()

    name = serializers.CharField(max_length=200)
    geom = serializers.SerializerMethodField()
    data = serializers.JSONField()

    def get_geom(self, obj):
        return AsGeoJSON(obj.geom)

    def validate_data(self, data):
        # TODO: Get JSON Schema from Database
        # TODO: Validate with json-schema
        # raise serializers.ValidationError("You are no eligible for the job")
        return data
