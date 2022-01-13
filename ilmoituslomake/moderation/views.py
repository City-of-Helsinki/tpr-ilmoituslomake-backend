import json
import sys

from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

# Permissions
from rest_framework.permissions import IsAdminUser

from rest_framework import status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import (
    UpdateAPIView,
    CreateAPIView,
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
from moderation.utils import get_query

#
# from base.models import Notification
from notification_form.models import Notification, NotificationImage
from moderation.models import ModeratedNotification, ModeratedNotificationImage

# from base.serializers import NotificationSerializer
# from notification_form.serializers import NotificationSerializer

#
from moderation.models import ModerationItem
from moderation.serializers import (
    ModerationItemSerializer,
    ModerationItemDetailSerializer,
    PrivateModeratedNotificationSerializer,
    ApproveModeratorSerializer,
    ChangeRequestSerializer,
)

from base.image_utils import (
    preprocess_images,
    update_preprocess_url,
    process_images,
    unpublish_images,
    unpublish_all_images,
)

from ilmoituslomake.settings import JWT_IMAGE_SECRET, PRIVATE_AZURE_READ_KEY

import jwt


# Create your views here.


def image_proxy(request, id, image):
    token = request.GET.get("token", "")
    try:
        decoded_token = jwt.decode(token, JWT_IMAGE_SECRET, algorithms=["HS256"])
        if decoded_token["id"] == id and decoded_token["image"] == image:
            response = HttpResponse()
            response["X-Accel-Redirect"] = (
                "/proxy/" + id + "/" + image + PRIVATE_AZURE_READ_KEY
            )
            return response
    except Exception as e:
        pass
    return HttpResponse(status=status.HTTP_403_FORBIDDEN)


class ModerationNotificationRetrieveView(RetrieveAPIView):
    """
    Returns a single Notification instance
    """

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = ModeratedNotification.objects.all()
    serializer_class = PrivateModeratedNotificationSerializer


class ModerationItemSearchListView(ListAPIView):
    """
    Search all closed moderation items

    """

    permission_classes = [IsAdminUser]
    queryset = ModerationItem.objects.all()
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


# Moderator Edit
class ModeratorEditCreateView(CreateAPIView):
    """
    Create a ModerationTask of type moderator_edit
    """

    permission_classes = [IsAdminUser]
    queryset = ModerationItem.objects.all()
    serializer_class = ChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        headers = None

        copy_data = request.data.copy()
        copy_data["category"] = "moderator_edit"

        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)

        if copy_data["item_type"] != "add":
            target_moderated_notification = get_object_or_404(
                ModeratedNotification, pk=copy_data["target"]
            )

        # set revision
        if copy_data["item_type"] not in ["change", "add", "delete"]:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        # request.data[]
        copy_data["status"] = "open"

        # Revalidate
        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)

        # Create
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


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

        if moderation_item.is_completed():
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator == request.user:
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif moderation_item.moderator != None:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
        #
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

        if moderation_item.is_completed():
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

        if moderation_item.is_completed():
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator != request.user:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        moderation_item.status = "rejected"
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

        if moderation_item.is_completed():
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

        if moderation_item.is_completed():
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

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = ModerationItem.objects.all()
    serializer_class = ModerationItemDetailSerializer

    def update(self, request, id=None, *args, **kwargs):
        moderation_item = get_object_or_404(ModerationItem, pk=id)

        serializer = self.get_serializer(moderation_item)

        if moderation_item.is_completed():
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if moderation_item.moderator != request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        if moderation_item.item_type == "delete":
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        moderation_item.status = "closed"

        try:
            # Validate moderator input
            notification_serializer = ApproveModeratorSerializer(
                data=request.data["data"]
            )
            notification_serializer.is_valid(raise_exception=True)
        except Exception as e:  # except Exception as e:
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        moderation_item.data = request.data["data"]

        #
        try:
            #
            notification = None
            # TODO: Fetch based on revision?
            if moderation_item.category not in ["change_request", "moderator_edit"]:
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
                    moderation_item.target = moderated_notification
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
                    moderation_item.target = moderated_notification
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
                moderated_notification.published = True
                moderated_notification.save()
                moderation_item.target = moderated_notification
                if (
                    moderation_item.category not in ["change_request", "moderator_edit"]
                    and notification
                ):
                    notification.save()
            # process images
            images = preprocess_images(request)
            if notification:
                images = update_preprocess_url(notification.pk, images)
            process_images(ModeratedNotificationImage, moderated_notification, images)
            unpublish_images(ModeratedNotificationImage, moderated_notification)
            #
            if (
                moderation_item.category not in ["change_request", "moderator_edit"]
                and notification
            ):
                unpublish_all_images(NotificationImage, notification)
        except Exception as e:
            print(e, file=sys.stderr)
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            moderation_item.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ModeratedNotificationSearchListView(ListAPIView):
    """
    Search notifications.
    """

    queryset = ModeratedNotification.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = PrivateModeratedNotificationSerializer
    # pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        lang = "fi"
        lang_finland = "fi"
        published = True
        #
        search = {
            "search_name": "",
            "search_address__contains": "",
            "data__ontology_ids__contains": [],
            "data__matko_ids__contains": [],
            "search_comments__contains": "",
            "published": True,
            "search_neighborhood": "",
        }

        search_data = {}
        if request.GET.get("q") and request.GET["q"].strip():
            try:
                search_data = json.loads(request.GET.get("q"))
            except Exception as e:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
        else:
            # return Response([], status=status.HTTP_200_OK)
            # Empty should return all
            pass

        # Set the name search language
        if "lang" in search_data:
            lang = "fi" if lang not in ["fi", "sv", "en"] else search_data["lang"]
            lang_finland = "fi" if lang not in ["fi", "sv"] else search_data["lang"]
            del search_data["lang"]

        keys = search.keys()

        # Delete None search words
        delete = [key for key in search if key not in search]
        # delete the key
        for key in delete:
            del search_data[key]

        query_string = ""
        if "search_name" in search_data:
            query_string = search_data["search_name"]
        found_entries = None

        if query_string == "":
            found_entries = ModeratedNotification.objects.all()
        else:
            entry_query = get_query(
                query_string,
                [
                    "data__name",
                ],
            )
            found_entries = ModeratedNotification.objects.filter(entry_query)

        if "search_name" in search_data:
            del search_data["search_name"]

        queryset = (
            found_entries.annotate(
                search_address=SearchVector(
                    KeyTextTransform(
                        "street",
                        KeyTextTransform(
                            lang_finland, KeyTextTransform("address", "data")
                        ),
                    )
                )
                + SearchVector(
                    KeyTextTransform(
                        "postal_code",
                        KeyTextTransform(
                            lang_finland, KeyTextTransform("address", "data")
                        ),
                    )
                )
                + SearchVector(
                    KeyTextTransform(
                        "post_office",
                        KeyTextTransform(
                            lang_finland, KeyTextTransform("address", "data")
                        ),
                    )
                )
            )
            .annotate(
                search_neighborhood=SearchVector(
                    KeyTextTransform(
                        "neighborhood",
                        KeyTextTransform(
                            lang_finland, KeyTextTransform("address", "data")
                        ),
                    )
                )
            )
            .annotate(
                search_comments=SearchVector(KeyTextTransform("comments", "data"))
            )
            .filter(**search_data)
        )

        pagination = PageNumberPagination()
        qs = pagination.paginate_queryset(queryset, request)
        serializer = PrivateModeratedNotificationSerializer(qs, many=True)
        return pagination.get_paginated_response(serializer.data)
