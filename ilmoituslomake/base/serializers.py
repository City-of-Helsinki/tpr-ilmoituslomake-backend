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
    Returns certificate data with multilingual fields.
    """
    class Meta:
        model = Certificate
        fields = (
            "id",
            "certificate_type",
            "name_fi",
            "name_sv",
            "name_en",
            "url_fi",
            "url_sv",
            "url_en",
            "displayed_in_myhelsinki",
        )
        read_only_fields = fields


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

