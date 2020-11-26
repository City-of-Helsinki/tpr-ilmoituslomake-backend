from django.shortcuts import render

# Permissions
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView

from rest_framework import filters
from django.db.models import Q

#
from moderation.models import ModerationItem
from moderation.serializers import ModerationItemSerializer

# Create your views here.


class ModerationItemListView(ListAPIView):
    """"""

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all().filter(
        Q(status="open") | Q(status="in_progress")
    )
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]
    serializer_class = ModerationItemSerializer
