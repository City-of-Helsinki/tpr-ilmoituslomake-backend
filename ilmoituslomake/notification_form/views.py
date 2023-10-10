from django.shortcuts import render, get_object_or_404

from base.image_utils import preprocess_images, process_images

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework import filters

#
from moderation.models import ModerationItem
from moderation.serializers import ChangeRequestSerializer

from notification_form.models import Notification, NotificationImage
from moderation.models import ModeratedNotification
from base.models import NotificationSchema, OntologyWord, MatkoWord

# from notification_form.serializers import NotificationImageSerializer
from base.serializers import (
    NotificationSchemaSerializer,
    OntologyWordSerializer,
    MatkoWordSerializer,
)
from moderation.serializers import (
    PublicModeratedNotificationSerializer,
    ModerationNotificationSerializer,
)

from django.db.models import Q
# from image_utils import preprocess_images, process_images   


class NotificationSchemaCreateView(CreateAPIView):
    """
    Create a Notification schema instance
    """

    permission_classes = [IsAdminUser]
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationSchemaUpdateView(UpdateAPIView):
    """
    Update a Notification schema instance
    """

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            serializer.data
        )

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class NotificationSchemaRetrieveView(RetrieveAPIView):
    """
    Returns the schema for form data
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer


class ChangeRequestCreateView(CreateAPIView):
    """
    Create a ModerationItem of type change_request
    """

    permission_classes = [AllowAny]
    queryset = ModerationItem.objects.all()
    serializer_class = ChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        headers = None

        copy_data = request.data.copy()
        copy_data["category"] = "change_request"

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


class NotificationCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = ModerationNotificationSerializer

    def create(self, request, *args, **kwargs):
        headers = None
        images = []

        moderated_notification = None
        target_notification = None
        item_status = "created"
        try:
            # TODO: In the future check permission
            if request.data["id"]:
                moderated_notification = ModeratedNotification.objects.get(
                    pk=request.data["id"]
                )
                if moderated_notification.notification_id > 0:
                    target_notification = Notification.objects.get(
                        pk=moderated_notification.notification_id
                    )
                    item_status = "modified"
        except Exception as e:
            target_notification = None

        # Serialize
        serializer = ModerationNotificationSerializer(
            instance=target_notification, data=request.data
        )  # self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Preprocess images
        images = preprocess_images(request)

        # Create
        self.perform_create(serializer, item_status, images)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, item_status, images):
        instance = serializer.save(user=self.request.user, status=item_status)
        try:
            process_images(NotificationImage, instance, images)
        except Exception as e:
            pass

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationRetrieveView(RetrieveAPIView):
    """
    Returns a single ModeratedNotification instance
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = PublicModeratedNotificationSerializer


class NotificationListView(ListAPIView):
    """
    Returns a collection of ModeratedNotification instances. Search support
    """

    permission_classes = [AllowAny]
    queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = PublicModeratedNotificationSerializer
    filter_backends = [filters.SearchFilter]
    # TODO: Create migration which generates indices for JSON data
    search_fields = ["data__name__fi", "data__name__sv", "data__name__en"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.order_by('-updated_at')  # change is here  >> sorted with order of 'updated_at'

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OntologyWordListView(ListAPIView):
    """
    Returns a collection of ontology words instances.
    """

    permission_classes = [AllowAny]
    queryset = OntologyWord.objects.all()
    serializer_class = OntologyWordSerializer
    pagination_class = None


class MatkoWordListView(ListAPIView):
    """
    Returns a collection of matko words instances.
    """

    permission_classes = [AllowAny]
    queryset = MatkoWord.objects.all()
    serializer_class = MatkoWordSerializer
    pagination_class = None
