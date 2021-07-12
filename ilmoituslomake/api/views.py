# import json
# from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404

# Permissions
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from rest_framework import filters

from rest_framework.pagination import PageNumberPagination

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from moderation.models import ModeratedNotification
from api.serializers import ApiModeratedNotificationSerializerV1
from api.serializers import TranslationSerializer
from api.models import TranslationTodo

from django.db.models import Q


class ApiRetrieveViewV1(RetrieveAPIView):
    """
    Returns a single ModeratedNotification instance
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = ApiModeratedNotificationSerializerV1

    def get(self, request, id=None, *args, **kwargs):
        lang = request.GET.get("language", "fi")
        moderated_notification = get_object_or_404(ModeratedNotification, pk=id)
        serializer = ApiModeratedNotificationSerializerV1(
            moderated_notification, context={"lang": lang}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ApiListViewV1(ListAPIView):
    """
    Returns a collection of ModeratedNotification instances. Search support
    """

    permission_classes = [AllowAny]
    queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = ApiModeratedNotificationSerializerV1
    filter_backends = [filters.SearchFilter]
    # TODO: Create migration which generates indices for JSON data
    search_fields = ["data__name__fi", "data__name__sv", "data__name__en"]


class TranslationTodoView(ListAPIView):
    """
    Returns translations
    """

    permission_classes = [AllowAny]
    queryset = TranslationTodo.objects.all()
    serializer_class = TranslationSerializer
    lookup_field = "id"
    pagination_class = None