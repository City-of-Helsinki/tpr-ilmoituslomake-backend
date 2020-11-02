from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView

#
from base.models import Notification, NotificationSchema
from base.serializers import NotificationSerializer, NotificationSchemaSerializer


# TODO: Remove
class HelloView(RetrieveAPIView):
    """
    A view that returns Hello! message in JSON.
    """

    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = {"message": "Hello world!"}
        return Response(content)


class ApiDemoView(RetrieveAPIView):
    """
    A view that returns a mock up of our dataformat
    """

    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = {
            "name": {"fi": "string", "sv": "string", "en": "string"},
            "external_source": "string",  ## ???
            "description": {"fi": "string", "sv": "string", "en": "string"},
            "location": {"type": "Point", "coordinates": [12, 34]},
            "street_address": "string",
            "postal_address": "string",
            "phone": "string",
            "fax": "string",
            "email": "string",
            "website": "string",
            "images": {
                "main": {
                    "url": "",
                    "caption": {"fi": "string", "sv": "string", "en": "string"},
                },
                "others": [],
            },
            "google_street_view": "string",
            "opening_times": {"regular": "???", "exceptions": "???"},
            "keywords": {"fi": ["string"], "sv": ["string"], "en": ["string"]},
        }
        return Response(content)


class NotificationSchemaCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

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

    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer


class NotificationCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
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


class NotificationRetrieveView(RetrieveAPIView):
    """
    Returns a single Notification instance
    """

    lookup_field = "id"
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes =


class NotificationListView(ListAPIView):
    """
    Returns a collection of Notification instances
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes =
