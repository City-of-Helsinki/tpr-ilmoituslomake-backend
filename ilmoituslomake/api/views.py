# import json
# from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404

# Permissions
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from moderation.models import ModeratedNotification
from api.serializers import ApiModeratedNotificationSerializer


class ApiRetrieveView(RetrieveAPIView):
    """
    Returns a single ModeratedNotification instance
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = ModeratedNotification.objects.all()
    serializer_class = ApiModeratedNotificationSerializer

    def get(self, request, id=None, *args, **kwargs):
        lang = request.GET.get("language", "fi")
        moderated_notification = get_object_or_404(ModeratedNotification, pk=id)
        serializer = ApiModeratedNotificationSerializer(
            moderated_notification, context={"lang": lang}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
