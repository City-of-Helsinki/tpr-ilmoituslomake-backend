import datetime

from rest_framework import serializers

from moderation.models import ModeratedNotification


class ApiModeratedNotificationSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    org_id = serializers.SerializerMethodField()

    def get_org_id(self, obj):
        return None

    dept_id = serializers.SerializerMethodField()

    def get_dept_id(self, obj):
        return None

    provider_type = serializers.SerializerMethodField()

    def get_provider_type(self, obj):
        return None

    organizer_type = serializers.SerializerMethodField()

    def get_organizer_type(self, obj):
        return None

    organizer_name = serializers.SerializerMethodField()

    def get_organizer_name(self, obj):
        return None

    data_source_url = serializers.SerializerMethodField()

    def get_data_source_url(self, obj):
        return None

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["name"].get(lang)

    short_description = serializers.SerializerMethodField()

    def get_short_description(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["description"]["short"].get(lang)

    description = serializers.SerializerMethodField()

    def get_description(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["description"]["long"].get(lang)

    ontologyword_ids = serializers.SerializerMethodField()

    def get_ontologyword_ids(self, obj):
        return obj.data["ontology_ids"]

    extra_searchwords = serializers.SerializerMethodField()

    def get_extra_searchwords(self, obj):
        return obj.data.get("extra_keywords", [])

    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        return []  # TODO:

    sources = serializers.SerializerMethodField()

    def get_sources(self, obj):
        return []  # TODO:

    latitude = serializers.SerializerMethodField()

    def get_latitude(self, obj):
        return obj.location.y

    longitude = serializers.SerializerMethodField()

    def get_longitude(self, obj):
        return obj.location.x

    street_address = serializers.SerializerMethodField()

    def get_street_address(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["address"][lang_finland].get("street")

    address_zip = serializers.SerializerMethodField()

    def get_address_zip(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["address"][lang_finland].get("postal_code")

    address_city = serializers.SerializerMethodField()

    def get_address_city(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["address"][lang_finland].get("post_office")

    neighborhood_id = serializers.SerializerMethodField()

    def get_neighborhood_id(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["address"][lang_finland].get("neighborhood_id")

    neighborhood = serializers.SerializerMethodField()

    def get_neighborhood(self, obj):
        lang = self.context.get("lang", "fi")
        lang_finland = "fi" if lang not in ["fi", "sv"] else lang
        return obj.data["address"][lang_finland].get("neighborhood")

    phone = serializers.SerializerMethodField()

    def get_phone(self, obj):
        return obj.data.get("phone")

    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.data.get("email")

    www = serializers.SerializerMethodField()

    def get_www(self, obj):
        lang = self.context.get("lang", "fi")
        return obj.data["website"].get(lang)

    images = serializers.SerializerMethodField()

    def get_images(self, obj):
        return []  # TODO:

    created_time = serializers.SerializerMethodField()

    def get_created_time(self, obj):
        return obj.created_at.strftime("%Y-%m-%dT%H:%M:%S")

    modified_time = serializers.SerializerMethodField()

    def get_modified_time(self, obj):
        return obj.updated_at.strftime("%Y-%m-%dT%H:%M:%S")

    openinghours = serializers.SerializerMethodField()

    def get_openinghours(self, obj):
        return []

    class Meta:
        model = ModeratedNotification
        fields = (
            "id",
            "org_id",
            "dept_id",
            "provider_type",
            "organizer_type",
            "organizer_name",
            "data_source_url",
            "name",
            "short_description",
            "description",
            "ontologyword_ids",
            "extra_searchwords",
            "tags",
            "sources",
            "latitude",
            "longitude",
            "street_address",
            "address_zip",
            "address_city",
            "neighborhood_id",
            "neighborhood",
            "phone",
            "email",
            "www",
            "images",
            "created_time",
            "modified_time",
            "openinghours",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ret
