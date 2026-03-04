from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from base.models import (
    NotificationSchema,
    OntologyWord,
    MatkoWord,
    IdMappingAll,
    IdMappingKaupunkialustaMaster,
    Certificate,
    CustomerCertificate,
)


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


class IdMappingAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdMappingAll
        fields = "__all__"


class IdMappingKaupunkialustaMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdMappingKaupunkialustaMaster
        fields = "__all__"


# TODO: This is temp
class NotificationSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSchema
        fields = ("id", "name", "schema")


class CertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for Certificate model.
    Returns certificate data with multilingual fields nested under 'certificatename' and 'url'.
    """
    certificatename = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_type",
            "certificatename",
            "url",
            "displayed_in_myhelsinki",
        )
        read_only_fields = fields

    def get_certificatename(self, obj):
        return {
            "fi": obj.name_fi,
            "sv": obj.name_sv,
            "en": obj.name_en,
        }

    def get_url(self, obj):
        return {
            "fi": obj.url_fi,
            "sv": obj.url_sv,
            "en": obj.url_en,
        }


class CustomerCertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerCertificate model.
    Handles the link between notifications and certificates.
    """
    certificate_details = CertificateSerializer(source='certificate', read_only=True)
    
    class Meta:
        model = CustomerCertificate
        fields = (
            "id",
            "notification_id",
            "certificate",
            "certificate_details",
            "custom_name",
        )

