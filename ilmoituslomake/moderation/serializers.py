from rest_framework import serializers
from moderation.models import ChangeRequest

import json
from jsonschema import validate


class ChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangeRequest
        fields = (
            "target",
            "target_revision",
            "change_type",
            "description",
            "contact_details",
            "status",
        )
        read_only_fields = (
            "target_revision",
            "status",
        )
