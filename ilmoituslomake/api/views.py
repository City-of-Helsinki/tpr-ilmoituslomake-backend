# import json
# from datetime import datetime, timedelta

from translation.serializers import TranslationDataSerializer
from translation.models import TranslationData, TranslationTask
from django.shortcuts import render, get_object_or_404

from ilmoituslomake.settings import API_KEY_CUSTOM_HEADER

# Permissions
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from rest_framework.pagination import LimitOffsetPagination

from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)

from base.models import MatkoWord, OntologyWord
from moderation.models import ModeratedNotification
from api.serializers import (
    ApiModeratedNotificationSerializerV1,
    ApiMatkoWordSerializerV1,
    ApiOntologyWordSerializerV1,
)

from django.db.models import Q

from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey


def request_has_api_key(request):
    try:
        if (API_KEY_CUSTOM_HEADER) in request.META:
            key = request.META[API_KEY_CUSTOM_HEADER].split()[-1]
            api_key = APIKey.objects.get_from_key(key)
            if api_key:
                return True
    except Exception as e:
        pass
    return False


def modify_translation_data(old_data, new_data):
    """
    Modifies the data to the correct format for the front-end.
    """
    old_data["name"] = new_data["name"]["lang"]
    old_data["short_description"] = new_data["description"]["short"]["lang"]
    old_data["description"] = new_data["description"]["long"]["lang"]
    for image in old_data["images"]:
        for translated_image in new_data["images"]:
            if image["uuid"] == translated_image["uuid"]:
                image["source"] = translated_image["source"]
                if "lang" in translated_image["alt_text"]:
                    image["alt_text"] = translated_image["alt_text"]["lang"]


class LargeResultsSetPagination(LimitOffsetPagination):
    default_limit = 200
    max_limit = 200


class ApiOntologyWordListViewV1(ListAPIView):
    """
    Returns a collection of ontology words instances.
    """

    permission_classes = [AllowAny]
    queryset = OntologyWord.objects.all()
    serializer_class = ApiOntologyWordSerializerV1
    pagination_class = None


class ApiMatkoWordListViewV1(ListAPIView):
    """
    Returns a collection of matko words instances.
    """

    permission_classes = [AllowAny]
    queryset = MatkoWord.objects.all()
    serializer_class = ApiMatkoWordSerializerV1
    pagination_class = None


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
        moderated_notification = get_object_or_404(
            ModeratedNotification, pk=id, published=True
        )

        has_api_key = request_has_api_key(request)

        # If language is finnish, swedish or english, works with the serializer
        if lang in ["fi", "sv", "en"]:

            if not moderated_notification.has_lang(lang):
                return Response(
                    "Ei löydy valitulla kielellä.", status=status.HTTP_404_NOT_FOUND
                )

            serializer = ApiModeratedNotificationSerializerV1(
                moderated_notification,
                context={"lang": lang, "has_api_key": has_api_key},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        # If language is not finnish, swedish or english, find the newest, published
        # translationdata matching to the target and language and replace name, short_description,
        # description and picture alt text with the translations.
        serializer = ApiModeratedNotificationSerializerV1(
            moderated_notification, context={"has_api_key": has_api_key}
        )
        modified_data = serializer.data
        translation_tasks = TranslationTask.objects.filter(target=id, language_to=lang)
        for task in sorted(translation_tasks, key=lambda x: x.id, reverse=True):
            translation_data = TranslationData.objects.filter(
                task_id=task.id, language=lang
            )
            if len(translation_data) > 0 and task.published:
                data_serializer = TranslationDataSerializer(translation_data[0])
                modify_translation_data(modified_data, data_serializer.data)
                return Response(modified_data, status=status.HTTP_200_OK)
        return Response("Ei löydy", status=status.HTTP_404_NOT_FOUND)


class ApiListViewV1(ListAPIView):
    """
    Returns a collection of ModeratedNotification instances. Search support
    """

    permission_classes = [AllowAny]
    # queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = ApiModeratedNotificationSerializerV1
    # pagination_class = LargeResultsSetPagination

    def list(self, request, *args, **kwargs):
        lang = self.request.GET.get("language", "fi")

        has_api_key = request_has_api_key(request)

        modified_data = []

        pagination = LargeResultsSetPagination()
        data = []
        if lang in ["fi", "sv", "en"]:
            key = "data__name__" + str(lang)
            data = ModeratedNotification.objects.all().filter(
                Q(published=True), ~Q(**{key: ""})
            )
        else:
            data = ModeratedNotification.objects.all().filter(Q(published=True))
        qs = pagination.paginate_queryset(data, request)
        serializer = ApiModeratedNotificationSerializerV1(
            qs, many=True, context={"lang": lang, "has_api_key": has_api_key}
        )

        modified_data = serializer.data

        # If language is not finnish, swedish or english, find the newest, published
        # translationdata matching to the target and language and replace name, short_description,
        # description and picture alt text with the translations.
        if lang in ["fi", "sv", "en"]:
            return pagination.get_paginated_response(modified_data)
        # return Response(modified_data, status=status.HTTP_200_OK)

        index = 0
        for moderation_item in modified_data:
            translation_tasks = TranslationTask.objects.filter(
                target=moderation_item["id"], language_to=lang
            )
            sorted_tasks = sorted(translation_tasks, key=lambda x: x.id, reverse=True)
            found = False
            for task in sorted_tasks:
                translation_objects = TranslationData.objects.filter(
                    task_id=task.id, language=lang
                )
                if not found and translation_objects.exists() and task.published:
                    data_serializer = TranslationDataSerializer(translation_objects[0])
                    found = True
                    modify_translation_data(moderation_item, data_serializer.data)
            # If no translations are found for the target for the language, remove it from the response.
            if not found:
                modified_data[index] = None
            index += 1

        # New pagination is needed there to be 200 entries on each page and the count to be correct
        modified_data = [i for i in modified_data if i]
        modified_data_ids = [task["id"] for task in modified_data]
        pagination = LargeResultsSetPagination()
        data = ModeratedNotification.objects.filter(pk__in=modified_data_ids)
        qs = pagination.paginate_queryset(data, request)

        return pagination.get_paginated_response(modified_data)
        # return Response([i for i in modified_data if i], status=status.HTTP_200_OK)
