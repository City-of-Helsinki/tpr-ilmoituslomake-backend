from django.shortcuts import render

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView

from rest_framework import filters
from django.db.models import Q

#
from base.models import Notification
from base.serializers import NotificationSerializer

# Create your views here.


class ModerationNotificationAPIListView(ListAPIView):
    """
    Returns a collection of Notification instances open for moderation
    """

    permission_classes = [AllowAny]  # TODO: Require authentication & authorization
    queryset = Notification.objects.all().filter(
        Q(status="created") | Q(status="modified")
    )
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]
    serializer_class = NotificationSerializer
