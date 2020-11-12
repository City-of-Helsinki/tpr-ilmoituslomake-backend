from django.shortcuts import render

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView

from rest_framework import filters
from django.db.models import Q

#
from moderation.models import ChangeRequest
from moderation.serializers import ChangeRequestSerializer

from base.models import Notification
from base.serializers import NotificationSerializer

# Create your views here.


class ChangeRequestListView(ListAPIView):
    """"""

    permission_classes = [AllowAny]
    queryset = ChangeRequest.objects.all().filter(status="open")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]
    serializer_class = ChangeRequestSerializer

    # TODO: Implement save()
    # Check if Notification exists
    # Check if authenticated


class ModerationNotificationListView(ListAPIView):
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
