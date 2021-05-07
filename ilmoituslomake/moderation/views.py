import json

from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404

# Permissions
from rest_framework.permissions import IsAdminUser

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

from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.fields.jsonb import KeyTextTransform

#
# from base.models import Notification
from notification_form.models import Notification
from moderation.models import ModeratedNotification

# from base.serializers import NotificationSerializer
# from notification_form.serializers import NotificationSerializer

#
from moderation.models import ModerationItem
from moderation.serializers import (
    ModerationItemSerializer,
    ModerationItemDetailSerializer,
    NotificationSerializer,
)

# Create your views here.


class NotificationRetrieveView(RetrieveAPIView):
    """
    Returns a single Notification instance
    """

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class ModerationItemSearchListView(ListAPIView):
    """
    Search all closed moderation items

    """

    permission_classes = [IsAdminUser]
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

    permission_classes = [IsAdminUser]
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

    permission_classes = [IsAdminUser]
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

    permission_classes = [IsAdminUser]
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

    permission_classes = [IsAdminUser]
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

    permission_classes = [IsAdminUser]
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


# Reject ModerationItem, not checked
class RejectModerationItemView(DestroyAPIView):
    """
    Reject moderation item (close it)
    """

    permission_classes = [IsAdminUser]
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

        #
        try:
            notification = moderation_item.target
            notification.status = "rejected"
            notification.save()
        except Exception as e:
            pass
        finally:
            pass

        return Response(None, status=status.HTTP_204_NO_CONTENT)


# Delete Notification -> Unpublish
class DeleteNotificationView(DestroyAPIView):

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = ModerationItem.objects.all()
    serializer_class = ModerationItemSerializer

    def delete(self, request, id=None, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)

        if moderation_item.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        # Only assigned moderator can delete
        if moderation_item.moderator != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        # Has target
        if moderation_item.target:
            moderaterated_notification = moderation_item.target
            moderaterated_notification.published = False
            moderation_item.status = "closed"
            moderaterated_notification.save()
            moderation_item.save()
            return Response(None, status=status.HTTP_201_CREATED)

        return Response(None, status=status.HTTP_400_BAD_REQUEST)


# Get or Save in progress, not checked -> this will be removed!
class ModerationItemRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    Save moderation item as a draft
    """

    permission_classes = [IsAdminUser]
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
        if type(request.data["data"]) is not dict:
            moderation_item.data = json.loads(request.data["data"])  # TODO: Validate
        else:
            moderation_item.data = request.data["data"]  # TODO: Validate

        moderation_item.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Approve
class ModerationItemUpdateView(UpdateAPIView):
    """
    Save moderation
    """

    # permission_classes = [IsAdminUser]
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

        if moderation_item.item_type == "delete":
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        moderation_item.status = "closed"

        if type(request.data["data"]) is not dict:
            moderation_item.data = json.loads(request.data["data"])  # TODO: Validate
        else:
            moderation_item.data = request.data["data"]  # TODO: Validate

        moderation_item.save()

        #
        try:
            #
            notification = None
            # TODO: Fetch based on revision?
            if moderation_item.category != "change_request":
                notification = moderation_item.notification_target
                notification.status = "approved"
            #
            # if moderation_item.item_type == "created":
            if not moderation_item.target:
                if notification:
                    moderated_notification = ModeratedNotification(
                        user=notification.user,
                        data=moderation_item.data,
                        published=True,
                        notification_id=notification.pk,
                    )
                    moderated_notification.save()
                    # Update notification
                    notification.moderated_notification_id = moderated_notification.pk
                    notification.save()
                else:
                    # TODO: IMAGES!
                    notification = Notification(
                        data=moderation_item.data, user=request.user, status="approved"
                    )
                    notification.save()
                    moderated_notification = ModeratedNotification(
                        user=notification.user,
                        data=moderation_item.data,
                        published=True,
                        notification_id=notification.pk,
                    )
                    moderated_notification.save()
                    # Update notification
                    notification.moderated_notification_id = moderated_notification.pk
                    notification.save()
            # elif moderation_item.item_type == "modified":
            elif moderation_item.target:
                # moderated_notification = ModeratedNotification.objects.get(
                #    pk=notification.moderated_notification_id
                # )
                moderated_notification = moderation_item.target
                moderated_notification.data = moderation_item.data
                moderated_notification.save()
                if moderation_item.category != "change_request" and notification:
                    notification.save()
        except ModeratedNotification.DoesNotExist:
            pass
        finally:
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationSearchListView(ListAPIView):
    """
    Search notifications.
    """

    permission_classes = [IsAdminUser]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        lang = "fi"
        #
        search = {
            "search_name__contains": "iip",
            "address": None,
            "keyword": None,
            "comments": None,
        }
        keys = search.keys()

        # Delete None search words
        delete = [key for key in search if search[key] == None]
        # delete the key
        for key in delete:
            del search[key]

        queryset = (
            ModeratedNotification.objects.annotate(
                search_name=SearchVector(
                    KeyTextTransform(lang, KeyTextTransform("name", "data"))
                )
            )
            .annotate(address=SearchVector(KeyTextTransform("address", "data")))
            .annotate(comments=SearchVector(KeyTextTransform("comments", "data")))
            .filter(**search)
        )
        # keyword?

        return queryset
