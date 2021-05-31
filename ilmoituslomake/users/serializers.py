from rest_framework import serializers
from users.models import User

# TODO: Check should we use get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_staff", "email")
        read_only_fields = fields


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_staff", "email")
        read_only_fields = fields
