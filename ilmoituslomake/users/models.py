from django.contrib.auth.models import AnonymousUser
from django.contrib.gis.db import models
from helusers.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from rest_framework.permissions import BasePermission


class Organization(models.Model):
    name = models.CharField(max_length=32)
    full_name = models.TextField(blank=True)
    identifier = JSONField()

    def __str__(self):
        return self.full_name


class User(AbstractUser):
    organization_membership = models.ForeignKey(
        Organization, null=True, related_name="members", on_delete=models.DO_NOTHING
    )
    is_translator = models.BooleanField(default=False)


class IsTranslatorUser(BasePermission):
    """
    Allows access only to translator users.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return bool(False)
        return bool(request.user and request.user.is_translator)
