from django.shortcuts import render

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny

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

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = {"message": "Hello world!"}
        return Response(content)


class ApiDemoView(RetrieveAPIView):
    """
    A view that returns a mock up of our dataformat
    """

    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = {
            "tpr_id": "???",
            "unit_id": "???",
            "contract_category": "???",
            "contract_subcategory": "???",
            "name": {"fi": "string", "sv": "string", "en": "string"},
            "external_source": "???",
            "description": {"fi": "string", "sv": "string", "en": "string"},
            "location": {"type": "Point", "coordinates": [12, 34]},
            "street_address": "string",
            "postal_address": "string",
            "phone": "string",
            "fax": "string",
            "email": "string",
            "website": {"fi": "string", "sv": "string", "en": "string"},
            "images": {
                "main": {
                    "url": "",
                    "caption": {"fi": "string", "sv": "string", "en": "string"},
                },
                "others": [],
            },
            "google_street_view": "string",
            "opening_times": {"regular": "???", "exceptions": "???"},
            "price": "???",
            "keywords": {"fi": ["string"], "sv": ["string"], "en": ["string"]},
            "comments": "string",
            "reporter": {
                "name": "string",
                "email": "string",
                "organization?": "string",
                "phone?": "string",
            },
            "updated_at": "string",
            "created_at": "string",
        }
        return Response(content)


class NotificationSchemaCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [IsAuthenticated]
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

    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer


class NotificationCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [IsAuthenticated]
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

    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes =


class NotificationListView(ListAPIView):
    """
    Returns a collection of Notification instances
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes =
