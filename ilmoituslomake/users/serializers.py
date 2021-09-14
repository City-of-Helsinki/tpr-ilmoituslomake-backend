from django.db.models import fields
from rest_framework import serializers
from users.models import User

# TODO: Check should we use get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_staff", "email", "is_translator")
        read_only_fields = fields


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_staff", "email")
        read_only_fields = fields


class TranslatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_translator", "email")
        read_only_fields = fields
    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     translator = {}
    #     translator["name"] = ret["first_name"] + " " + ret["last_name"]
    #     translator["email"] = ret["email"]
    #     return translator


class TranslatorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_translator", "email", "uuid")
        read_only_fields = fields
