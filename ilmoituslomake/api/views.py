# import json
# from datetime import datetime, timedelta

from translation.serializers import TranslationDataSerializer
from translation.models import TranslationData, TranslationTask
from django.shortcuts import render, get_object_or_404
from django.utils import translation

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
        if lang == "fi" or lang == "sv" or lang == "en":
            serializer = ApiModeratedNotificationSerializerV1(
                moderated_notification, context={"lang": lang}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = ApiModeratedNotificationSerializerV1(
                moderated_notification
            )
            modified_data = serializer.data
            translation_tasks = TranslationTask.objects.filter(target = id, language_to = lang)
            for task in translation_tasks:
                translation_data = TranslationData.objects.filter(task_id = task.id)
                if len(translation_data) > 0:
                    if task.published:
                        data_serializer = TranslationDataSerializer(
                            translation_data[0]
                        )
                        modified_data["name"] = data_serializer.data["name"]["lang"]
                        modified_data["short_description"] = data_serializer.data["description"]["short"]["lang"]
                        modified_data["description"] = data_serializer.data["description"]["long"]["lang"]
                        for image in modified_data["images"]:
                            for translated_image in data_serializer.data["images"]:
                                if image["uuid"] == translated_image["uuid"]:
                                    image["source"] = translated_image["source"]
                                    image["alt_text"] = translated_image["alt_text"]
                        return Response(modified_data, status=status.HTTP_200_OK)
            return Response(None, status=status.HTTP_404_NOT_FOUND)


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
