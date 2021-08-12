from translation.serializers import TranslationTaskSerializer, ChangeRequestSerializer
from translation.models import TranslationTask
from django.shortcuts import render
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView
)
from rest_framework import filters, serializers
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response

from rest_framework.permissions import IsAdminUser

from rest_framework import status
from moderation.models import ModeratedNotification
# Create your views here.
class TranslationTaskListView(ListAPIView):
    """
    Show all moderation items

    """

    # permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-moderator", "-created_at"]
    serializer_class = TranslationTaskSerializer


class TranslationEditCreateView(CreateAPIView):
    """
    Create a ModerationTask of type moderator_edit
    """

    #permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    serializer_class = ChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        # targets: selectedPlaces.map((place) => place.id),
        # language,
        # message,
        # translator,
        headers = None
        
        copy_data = request.data.copy()
        copy_data["category"] = "translation_edit"
        copy_data["requestId"] = 1
        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)
        
        
    
        # request.data[]
        copy_data["status"] = "open"
        print(copy_data)
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