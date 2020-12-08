import json

from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404

# Permissions
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    UpdateAPIView,
    ListAPIView,
    DestroyAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
)

from rest_framework import filters
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

#
from base.models import Notification
from base.serializers import NotificationSerializer

#
from moderation.models import ModerationItem
from moderation.serializers import (
    ModerationItemSerializer,
    ModerationItemDetailSerializer,
)

# Create your views here.


class ModerationItemSearchListView(ListAPIView):
    """
    Search all closed moderation items

    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all().filter(~Q(status="closed"))
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = (
        "target__data__name__fi",
        "target__data__name__sv",
        "target__data__name__en",
        "target__id",
    )
    filter_fields = ("category",)
    serializer_class = ModerationItemSerializer


class NewModerationItemListView(ListAPIView):
    """"""

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    serializer_class = ModerationItemSerializer

    def get_queryset(self):
        time_threshold = datetime.now() - timedelta(hours=72)
        return ModerationItem.objects.all().filter(
            Q(moderator=None), Q(created_at__gt=time_threshold), Q(status="open")
        )


class ModerationItemListView(ListAPIView):
    """
    Show all moderation items

    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all().filter(
        Q(status="open") | Q(status="in_progress")
    )
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-moderator", "-created_at"]
    serializer_class = ModerationItemSerializer


class MyModerationItemListView(ListAPIView):
    """
    Show all current user's moderation items
    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    serializer_class = ModerationItemSerializer

    def get_queryset(self):
        return ModerationItem.objects.all().filter(
            Q(moderator=self.request.user), ~Q(status="closed")
        )


# Assign
class AssignModerationItemView(UpdateAPIView):
    """
    Assign moderation item to the current user
    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all()
    serializer_class = ModerationItemSerializer

    def update(self, request, id=None, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)

        serializer = self.get_serializer(moderation_item)

        if moderation_item.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator != None:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        moderation_item.moderator = request.user
        moderation_item.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Unassign
class UnassignModerationItemView(UpdateAPIView):
    """
    Unassign moderation item

    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all()
    serializer_class = ModerationItemSerializer

    def update(self, request, id=None, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)

        serializer = self.get_serializer(moderation_item)

        if moderation_item.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator != None:
            moderation_item.moderator = None
            moderation_item.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_304_NOT_MODIFIED)


# Reject ModerationItem
class RejectModerationItemView(DestroyAPIView):
    """
    Reject moderation item (close it)
    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all()
    serializer_class = ModerationItemSerializer

    def delete(self, request, id=None, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)

        serializer = self.get_serializer(moderation_item)

        if moderation_item.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator != request.user:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        moderation_item.status = "closed"
        moderation_item.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


# Delete Notification
# class DeleteNotificationView(DestroyAPIView):

#     permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
#     queryset = Notification.objects.all().filter()
#     serializer_class = NotificationSerializer

#     def delete(self, request, id, *args, **kwargs):
#         moderation_item = get_object_or_404(ModerationItem, pk=id)
#         # Only assigned moderator can delete
#         if moderation_item.moderator != request.user:
#             pass
#         moderation_item.delete()
#         pass

# Get or Save in progress
class ModerationItemRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    Save moderation item as a draft
    """

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    lookup_field = "id"
    queryset = ModerationItem.objects.all()
    serializer_class = ModerationItemDetailSerializer

    def update(self, request, id=None, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)

        serializer = self.get_serializer(moderation_item)

        if moderation_item.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        moderation_item.status = "in_progress"
        moderation_item.data = json.loads(request.data["data"])  # TODO: Validate

        moderation_item.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Save
