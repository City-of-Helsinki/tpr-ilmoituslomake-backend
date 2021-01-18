from django.shortcuts import render, get_object_or_404

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

from base.models import Notification, NotificationSchema, OntologyWord
from base.serializers import (
    NotificationSerializer,
    NotificationSchemaSerializer,
    OntologyWordSerializer,
)
from notification_form.serializers import ToimipisterekisteriNotificationAPISerializer

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


# TODO: Remove once authentication is implemented
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class NotificationCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [AllowAny]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # TODO: Remove once authentication is implemented
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def create(self, request, *args, **kwargs):
        headers = None
        is_update = False
        instance = None
        images = []
        # Serialize
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Handle images
        data_images = request.data["data"]["images"]
        if "images" in request.data:
            images = request.data["images"]  # validate
            del request.data["images"]

        if len(images) > 0:
            # if permmission = false?
            # images: [{ index: <some number>, base64: "data:image/jpeg;base64,<blah...>"}]
            # Handle base64 image
            for i in range(len(images)):
                image_idx = images[i]["index"]
                for image in data_images:
                    if image["index"] == image_idx:
                        data_image = data_images[image_idx]
                        base64 = images[i]["base64"]
                        # handle base64 data, how to refer to this data?
                        request.data["data"]["images"][image_idx][
                            "url"
                        ] = "https://edit.myhelsinki.fi/sites/default/files/styles/square_600/public/2020-05/espa_x.jpg"
                        break
            # Create
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
        else:
            # Create
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

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
    Returns a collection of Notification instances. Search support
    """

    permission_classes = [AllowAny]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [filters.SearchFilter]
    # TODO: Add more search fields
    # TODO: Create migration which generates indices for JSON data
    search_fields = ["data__name__fi"]


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


## ToimipisterekisteriAPI views


class ToimipisterekisteriNotificationAPIRetrieveView(RetrieveAPIView):
    """
    Returns a single Notification for ToimipisterekisteriAPI
    """

    permission_classes = [AllowAny]  # TODO: Require authentication & authorization
    lookup_field = "id"
    queryset = Notification.objects.all()
    serializer_class = ToimipisterekisteriNotificationAPISerializer


class ToimipisterekisteriNotificationAPIListView(ListAPIView):
    """
    Returns a collection of Notification instances for ToimipisterekisteriAPI
    """

    permission_classes = [AllowAny]  # TODO: Require authentication & authorization
    queryset = Notification.objects.all()
    serializer_class = ToimipisterekisteriNotificationAPISerializer
