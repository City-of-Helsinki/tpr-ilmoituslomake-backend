from rest_framework import serializers
from users.models import User

# TODO: Check should we use get_user_model()
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        read_only_fields = fields


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        read_only_fields = fields


# {
#    "id": 1,
#    "password": "<hash>",
#    "last_login": "2020-11-02T14:54:40.226499Z",
#    "is_superuser": false,
#    "username": "",
#    "first_name": "",
#    "last_name": "",
#    "email": "",
#    "is_staff": true,
#    "is_active": true,
#    "date_joined": "2020-11-02T14:19:07.665570Z",
#    "uuid": "<uuid>",
#    "department_name": null,
#    "groups": [],
#    "user_permissions": [],
#    "ad_groups": []
# }
