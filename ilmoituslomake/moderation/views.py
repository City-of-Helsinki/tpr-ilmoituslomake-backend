from django.shortcuts import render

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView

#
from base.models import Notification

# Create your views here.


class ModerationNotificationAPIListView(ListAPIView):
    """
    Returns a collection of Notification instances open for moderation
    """

    permission_classes = [AllowAny]  # TODO: Require authentication & authorization
    queryset = Notification.objects.all()
    # serializer_class = ToimipisterekisteriNotificationAPISerializer
