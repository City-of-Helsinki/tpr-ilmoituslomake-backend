import base64
import uuid
import io
import requests
from PIL import Image

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

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
from base.models import NotificationSchema, OntologyWord

from notification_form.serializers import NotificationImageSerializer
from base.serializers import (
    NotificationSchemaSerializer,
    OntologyWordSerializer,
)
from moderation.serializers import (
    PublicModeratedNotificationSerializer,
    NotificationSerializer,
)

from django.db.models import Q

# TODO: Remove
class NotificationSchemaCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [AllowAny]
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer
    # permission_classes =

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


class NotificationSchemaRetrieveView(RetrieveAPIView):
    """
    Returns the schema for form data
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer


# Handle this!
class ChangeRequestCreateView(CreateAPIView):
    """
    Create a ModerationItem of type change_request
    """

    permission_classes = [AllowAny]
    queryset = ModerationItem.objects.all()
    serializer_class = ChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        headers = None
        # Serialize
        # request.data["target_revision"] = -1

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.data["item_type"] != "add":
            target_moderated_notification = get_object_or_404(
                ModeratedNotification, pk=request.data["moderated_notification_id"]
            )
            if target_moderated_notification.notification_id > 0:
                target_notification = get_object_or_404(
                    Notification, pk=target_moderated_notification.notification_id
                )
                # TODO: Add target_notification to target, look info form createnotification

        # set revision
        # request.data["target_revision"] = -1

        if request.data["item_type"] not in ["change", "add", "delete"]:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        # request.data[]
        request.data["status"] = "open"

        # Revalidate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationUpdateView(UpdateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        pass


class NotificationCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        headers = None
        request_images = []
        image_uploads = []

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
        serializer = NotificationSerializer(
            instance=target_notification, data=request.data
        )  # self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if False:
            # Create
            self.perform_create(serializer, item_status, image_uploads)
            headers = self.get_success_headers(serializer.data)
        else:
            # Create
            self.perform_create(serializer, item_status, [])
            headers = self.get_success_headers(serializer.data)

        # TODO: Yhteenveto
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, item_status, image_uploads):
        instance = serializer.save(user=self.request.user, status=item_status)
        # TODO: What if not an image
        data = None
        for upload in image_uploads:
            if upload["base64"] != "":
                data = base64.b64decode(upload["base64"].split(",")[1])
                # print(upload["base64"][0:64])
                del upload["base64"]
            elif upload["url"] != "":
                response = requests.get(upload["url"], stream=True)
                if response.status_code == 200:
                    response.raw.decode_content = True
                    data = response.raw.read()
                else:
                    continue
            else:
                continue
            # TODO: Virus check
            # check
            #
            if data != None:
                image = Image.open(io.BytesIO(data))
                with io.BytesIO() as output:
                    # print(output)
                    image.save(output, format="JPEG")
                    upload["data"] = ContentFile(output.getvalue())
            else:
                continue
            #
            notif_image = NotificationImage(
                filename=upload["filename"],
                data=InMemoryUploadedFile(
                    upload["data"],
                    None,  # field_name
                    upload["filename"],  # file name
                    "image/jpeg",  # content_type
                    upload["data"].tell,  # size
                    None,  # content_type_extra
                ),
                notification=instance,
                metadata=upload["metadata"],
            )
            notif_image.save()

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


class OntologyWordListView(ListAPIView):
    """
    Returns a collection of ontology words instances. Search support
    """

    permission_classes = [AllowAny]
    queryset = OntologyWord.objects.all()
    serializer_class = OntologyWordSerializer
    # filter_backends = [filters.SearchFilter]
    # TODO: Add more search fields
    # TODO: Create migration which generates indices for JSON data
    # search_fields = ["data__ontologyword__fi"]
    pagination_class = None


# def images(request):
#     if request.user.is_authenticated():
#         response = HttpResponse()
#         response['X-Accel-Redirect'] = '/tpr-notification-dev/'
#         return response
#     return Response(None, status=status.HTTP_404_NOT_FOUND)
