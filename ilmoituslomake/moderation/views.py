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

# TODO: Conver to new moderation
class ModerationItemListView(ListAPIView):
    """"""

    permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
    queryset = ModerationItem.objects.all().filter(Q(status="open"))
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
    queryset = ModerationItem.objects.all().filter()
    serializer_class = ModerationItemSerializer

    def update(self, request, id, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)
        if moderation_item.moderator != None:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        moderation_item.moderator = request.user

        serializer = self.get_serializer(data=moderation_item)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)

        moderation_item.save()
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        # return Response(
        #     serializer.data, status=status.HTTP_201_CREATED, headers=headers
        # )


# Unassign
# class UnassignModerationItemView(UpdateAPIView):

#     permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
#     queryset = ModerationItem.objects.all().filter()
#     serializer_class = ModerationItemDetailSerializer

#     def update(self, request, id, *args, **kwargs):
#         moderation_item = get_object_or_404(ModerationItem, pk=id)
#         moderation_item.moderator = None
#         moderation_item.save()
#         pass

# Reject ModerationItem
# class RejectModerationItemView(DestroyAPIView):

#     permission_classes = [IsAuthenticated]  # TODO: Require user to be a moderator
#     queryset = ModerationItem.objects.all().filter()
#     serializer_class = ModerationItemDetailSerializer

#     def delete(self, request, id, *args, **kwargs):
#         moderation_item = get_object_or_404(ModerationItem, pk=id)
#         # Only assigned moderator can reject
#         if moderation_item.moderator != request.user:
#             pass
#         moderation_item.delete()
#         pass

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
