import base64
import uuid
import io
import requests
from PIL import Image


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
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView
from rest_framework import filters

#
from moderation.models import ModerationItem
from moderation.serializers import ChangeRequestSerializer

from notification_form.models import Notification
from moderation.models import ModeratedNotification
from base.models import NotificationSchema, OntologyWord, NotificationImage

from base.serializers import (
    NotificationSerializer,
    NotificationSchemaSerializer,
    OntologyWordSerializer,
)
from moderation.serializers import PublicModeratedNotificationSerializer

#
from rest_framework.authentication import SessionAuthentication, BasicAuthentication


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
            target_notification = get_object_or_404(
                Notification, pk=request.data["target"]
            )
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

        # Serialize
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Handle images
        data_images = request.data["data"]["images"]
        if "images" in request.data:
            request_images = request.data["images"]  # validate
            # del request.data["images"]

        if len(request_images) > 0:
            # if permission = false?
            # images: [{ index: <some number>, base64: "data:image/jpeg;base64,<blah...>"}]
            # Handle base64 image
            for i in range(len(request_images)):
                image_idx = request_images[i]["uuid"]
                for idx in range(len(data_images)):  # image in data_images:
                    image = data_images[idx]
                    if image["uuid"] == image_idx:
                        data_image = data_images[idx]
                        #  image = base64.b64decode(str('stringdata'))

                        image_uploads.append(
                            {
                                "filename": str(image_idx) + ".jpg",
                                "base64": request_images[i]["base64"]
                                if ("base64" in request_images[i])
                                else "",
                                "url": request_images[i]["url"]
                                if ("url" in request_images[i])
                                else "",
                                "metadata": data_image,
                            }
                        )
                        break
            # Create
            self.perform_create(serializer, image_uploads)
            headers = self.get_success_headers(serializer.data)
        else:
            # Create
            self.perform_create(serializer, [])
            headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, image_uploads):
        instance = serializer.save(user=self.request.user)
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
    Returns a single Notification instance
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class NotificationListView(ListAPIView):
    """
    Returns a collection of ModeratedNotification instances. Search support
    """

    permission_classes = [AllowAny]
    queryset = ModeratedNotification.objects.all()
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
