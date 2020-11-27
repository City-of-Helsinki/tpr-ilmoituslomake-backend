from django.shortcuts import render, get_object_or_404

# Permissions
from rest_framework.permissions import IsAuthenticated

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView, ListAPIView, DestroyAPIView

from rest_framework import filters
from django.db.models import Q

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


class NewModerationItemListView(ListAPIView):
    """"""

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all().filter(Q(moderator=None), Q(status="open"))
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["updated_at"]
    ordering = ["-updated_at"]
    serializer_class = ModerationItemSerializer


# TODO: Convert to all open ones
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


# Assign
class AssignModerationItemView(UpdateAPIView):

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

# Save in progress
# Save
