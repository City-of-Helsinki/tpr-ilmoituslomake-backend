from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from base.models import NotificationSchema, OntologyWord, MatkoWord


class OntologyWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = OntologyWord
        fields = ("data",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret["data"]


class MatkoWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatkoWord
        fields = ("data",)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret["data"]


# TODO: This is temp
class NotificationSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSchema
        fields = ("id", "name", "schema")
