from translation.serializers import TranslationTaskSerializer
from translation.models import TranslationTask
from django.shortcuts import render
from rest_framework.generics import (
    ListAPIView
)
from rest_framework import filters, serializers
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