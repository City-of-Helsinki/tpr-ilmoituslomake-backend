from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, ListAPIView, CreateAPIView

#
from base.models import Notification
from base.serializers import NotificationSerializer


# TODO: Remove
class HelloView(RetrieveAPIView):
    """
    A view that returns Hello! message in JSON.
    """

    renderer_classes = [JSONRenderer]

    def get(self, request):
        content = {"message": "Hello world!"}
        return Response(content)


class FormSchemaView(RetrieveAPIView):
    """
    Returns the schema for form data
    """

    # TODO: Get from database
    def get(self, request):
        content = {
            "$id": "<url>",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "<description>",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "street_address": {"type": "string"},
                "postal_address": {"type": "string"},
            },
            "required": ["name", "street_address", "postal_address"],
        }
        return Response(content)


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

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes =

    def get(self, request):
        queryset = self.get_queryset()
        serializer = NotificationSerializer(queryset)
        return Response(serializer.data)


class NotificationListView(ListAPIView):
    """
    Returns a collection of Notification instances
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    # permission_classes =

    def list(self, request):
        queryset = self.get_queryset()
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data)
