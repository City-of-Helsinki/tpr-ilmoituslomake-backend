from copy import error
from users.serializers import UserSerializer
from users.models import IsTranslatorUser, User
import json
from translation.serializers import TranslationDataSerializer, TranslationTaskWithDataSerializer, TranslationTaskSerializer, ChangeRequestSerializer, TranslationRequestSerializer
from translation.models import TranslationData, TranslationTask
from django.shortcuts import get_object_or_404, render
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView
)
from rest_framework import filters, serializers
from django.shortcuts import render, get_list_or_404
from rest_framework.response import Response
from django.http.response import HttpResponse
from rest_framework.permissions import IsAdminUser

from rest_framework import status
from moderation.models import ModeratedNotification
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
class TranslationTaskListView(ListAPIView):
    """
    Show all moderation items

    """

    permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at"]
    ordering = ["-moderator", "-created_at"]
    serializer_class = TranslationTaskSerializer


class TranslationRequestEditCreateView(CreateAPIView):
    """
    Create a ModerationTask of type moderator_edit
    """

    permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    serializer_class = ChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        '''
        If a translation request exists, modifies it. Otherwise
        creates a new translation request.
        '''
        request_data = request.data.copy()

        # If a request already exists, modify the old
        if "id" in request_data.keys():
            old_tasks = TranslationTask.objects.filter(request_id = request_data["id"])
            for task in old_tasks:
                task.translator = request_data["translator"]
                task.message = request_data["message"]
                task.save()
            return Response(
                {"id": request_data["id"]}, status=status.HTTP_201_CREATED
            )

        request_id = 1
        new_request_id = 1
        if len(TranslationTask.objects.all()) > 0:
            new_request_id = TranslationTask.objects.all().order_by("-request_id")[0].request_id + 1

        headers = None

        # Creates a new translation task entry
        # for every target in the request
        for item in request_data["targets"]:
            copy_data = {}
            copy_data["category"] = "translation_task"
            if "id" in request_data.keys():
                copy_data["request_id"] = request_data["id"]
            else:
                copy_data["request_id"] = new_request_id
            copy_data["target"] = item
            copy_data["language_from"] = request_data["language"]["from"]
            copy_data["language_to"] = request_data["language"]["to"]
            copy_data["translator"] = request_data["translator"]
            copy_data["message"] = request_data["message"]
            serializer = self.get_serializer(data=copy_data)
            serializer.is_valid(raise_exception=True)

            copy_data["status"] = "open"
            # Revalidate
            serializer = self.get_serializer(data=copy_data)
            serializer.is_valid(raise_exception=True)

            # Create
            translation_task = serializer.save()
            translation_task.moderator = request.user
            translation_task.save()
            headers = self.get_success_headers(serializer.data)

            request_id = copy_data["request_id"]

        return Response(
            {"id": request_id}, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class TranslationTaskRetrieveByRequestIdView(RetrieveAPIView):
    lookup_field = "id"
    queryset = TranslationTask.objects.all()
    serializer_class = TranslationTaskSerializer

    def get(self, request, request_id=None, *args, **kwargs):
        '''
        Returns all translation task objects with some request_id
        '''
        serializer = TranslationTaskSerializer(
            TranslationTask.objects.all(), many=True, context={"request_id": request_id}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TranslationTodoRetrieveView(RetrieveAPIView):
    lookup_field = "id"
    queryset = TranslationTask.objects.all()
    serializer_class = TranslationTaskWithDataSerializer
    permission_classes = [IsTranslatorUser]

    def get(self, request, id=None, *args, **kwargs):
        '''
        Returns all translation task objects with some id
        '''
        if not request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        translation_task = get_object_or_404(TranslationTask, id=id)

        if translation_task.translator["email"] != request.user.email:
            return Response(None, status=status.HTTP_403_FORBIDDEN)

        serializer = TranslationTaskWithDataSerializer(
            translation_task, context={"id": id}
        )
        ret = serializer.data
        return Response(ret, status=status.HTTP_200_OK)


class TranslationTaskRetrieveView(RetrieveAPIView):
    lookup_field = "id"
    queryset = TranslationTask.objects.all()
    serializer_class = TranslationTaskWithDataSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, id=None, *args, **kwargs):
        '''
        Returns all translation task objects with some id
        '''
        translation_task = get_object_or_404(TranslationTask, id=id)
        serializer = TranslationTaskWithDataSerializer(
            translation_task, context={"id": id}
        )
        ret = serializer.data
        return Response(ret, status=status.HTTP_200_OK)


class TranslationRequestRetrieveView(RetrieveAPIView):

    permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    def get(self, request, request_id, *args, **kwargs):
        serializer = TranslationTaskSerializer(
            TranslationTask.objects.filter(request_id=request_id), many=True, context={"request_id": request_id}
        )

        data = serializer.data
        if len(data) == 0:
            return Response([], status=status.HTTP_200_OK)

        first_task = data[0]
        base = {
            "id": first_task["requestId"],
            "request": first_task["created_at"],
            "language": first_task["language"],
            "message": first_task["message"],
            "tasks": [],
            "category": first_task["category"],
            "item_type": first_task["item_type"],
            "translator": first_task["translator"],
            "moderator": first_task["moderator"],
            "created_at": first_task["created_at"],
            "updated_at":  first_task["updated_at"],

        }

        for item in serializer.data:
            single_task = {
                "id": item["id"],
                "target": {
                    "id": item["target"]["id"],
                    "name": item["target"]["name"]
                },
                "status":  item["status"]
            }
            base["tasks"].append(single_task)


        return Response(base, status=status.HTTP_200_OK)


class TranslationTaskSearchListView(ListAPIView):
    """
    Search all closed moderation items

    """

    permission_classes = [IsTranslatorUser]
    serializer_class = TranslationTaskSerializer
    def get_queryset(self):
        user = self.request.user
        temp = {
                "name": user.first_name,
                "email": user.email,
            },
        return TranslationTask.objects.all()
    # queryset = TranslationTask.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = (
        "target__data__name__fi",
        "target__data__name__sv",
        "target__data__name__en",
        "target__id",
    )
    filter_fields = ("category",)


class ModerationTranslationTaskSearchListView(ListAPIView):
    """
    Search all closed moderation items

    """

    permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = (
        "target__data__name__fi",
        "target__data__name__sv",
        "target__data__name__en",
        "target__id",
    )
    filter_fields = ("category",)
    serializer_class = TranslationTaskSerializer


class TranslationRequestSearchListView(ListAPIView):
    """
    Search all closed moderation items

    """

    permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = (
        "target__data__name__fi",
        "target__data__name__sv",
        "target__data__name__en",
        "target__id",
    )
    filter_fields = ("category",)
    serializer_class = TranslationRequestSerializer


class TranslationTaskEditCreateView(UpdateAPIView):
    """
    Update TranslationTask view for Translator
    """

    permission_classes = [IsTranslatorUser]
    lookup_field = "id"
    queryset = TranslationTask.objects.all()
    serializer_class = TranslationTaskWithDataSerializer

    def update(self, request, id=None, *args, **kwargs):
        translation_task = get_object_or_404(TranslationTask, pk=id)

        serializer = self.get_serializer(translation_task)

        if translation_task.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        if translation_task.translator.email != request.user.email:
            return Response(None, status=status.HTTP_403_FORBIDDEN)
            
        if request.data["draft"]:
            translation_task.status = "in_progress"
            translation_task.published = False
        else:
            translation_task.status = "closed"
            translation_task.published = True

        translation_task_data = {}
        if type(request.data["data"]) is not dict:
            translation_task_data = json.loads(request.data["data"])  # TODO: Validate
        else:
            translation_task_data = request.data["data"]  # TODO: Validate

        old_translation_data = TranslationData.objects.filter(task_id = id)
        if len(old_translation_data) > 0:
            old_translation_data[0].images = translation_task_data["images"]
            old_translation_data[0].name = translation_task_data["name"]["lang"]
            old_translation_data[0].language = translation_task_data["language"]
            old_translation_data[0].description_short = translation_task_data["description"]["short"]["lang"]
            old_translation_data[0].description_long = translation_task_data["description"]["long"]["lang"]
            old_translation_data[0].website = translation_task_data["website"]["lang"]
            old_translation_data[0].save()
        else:
            new_data = {}
            new_data["task_id"] = translation_task
            new_data["images"] = translation_task_data["images"]
            new_data["name"] = translation_task_data["name"]["lang"]
            new_data["language"] = translation_task_data["language"]
            new_data["description_short"] = translation_task_data["description"]["short"]["lang"]
            new_data["description_long"] = translation_task_data["description"]["long"]["lang"]
            new_data["website"] = translation_task_data["website"]["lang"]
            translation_data = TranslationData(**new_data)
            translation_data.save()

        translation_task.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ModerationTranslationTaskEditCreateView(UpdateAPIView):
    """
    Update TranslationTask view for Moderator
    """

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = TranslationTask.objects.all()
    serializer_class = TranslationTaskWithDataSerializer

    def update(self, request, id=None, *args, **kwargs):
        translation_task = get_object_or_404(TranslationTask, pk=id)

        serializer = self.get_serializer(translation_task)

        if translation_task.status == "closed":
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        # if translation_task.moderator != request.user:
        #     return Response(None, status=status.HTTP_403_FORBIDDEN)
        
        if request.data["draft"]:
            translation_task.status = "in_progress"
            translation_task.published = False
        else:
            translation_task.status = "closed"
            translation_task.published = True

        translation_task_data = {}
        if type(request.data["data"]) is not dict:
            translation_task_data = json.loads(request.data["data"])  # TODO: Validate
        else:
            translation_task_data = request.data["data"]  # TODO: Validate

        old_translation_data = TranslationData.objects.filter(task_id = id)
        if len(old_translation_data) > 0:
            old_translation_data[0].images = translation_task_data["images"]
            old_translation_data[0].name = translation_task_data["name"]["lang"]
            old_translation_data[0].language = translation_task_data["language"]
            old_translation_data[0].description_short = translation_task_data["description"]["short"]["lang"]
            old_translation_data[0].description_long = translation_task_data["description"]["long"]["lang"]
            old_translation_data[0].website = translation_task_data["website"]["lang"]
            old_translation_data[0].save()
        else:
            new_data = {}
            new_data["task_id"] = translation_task
            new_data["images"] = translation_task_data["images"]
            new_data["name"] = translation_task_data["name"]["lang"]
            new_data["language"] = translation_task_data["language"]
            new_data["description_short"] = translation_task_data["description"]["short"]["lang"]
            new_data["description_long"] = translation_task_data["description"]["long"]["lang"]
            new_data["website"] = translation_task_data["website"]["lang"]
            translation_data = TranslationData(**new_data)
            translation_data.save()

        translation_task.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TranslationDataListView(ListAPIView):
    """
    View for debugging translation data

    """

    permission_classes = [IsAdminUser]
    queryset = TranslationData.objects.all()
    filter_backends = [filters.OrderingFilter]
    serializer_class = TranslationDataSerializer


class ModerationTranslationRequestDeleteView(DestroyAPIView):

    permission_classes = [IsAdminUser]
    queryset = TranslationTask.objects.all()
    serializer_class = ChangeRequestSerializer
    
    def delete(self, request, id=None, *args, **kwargs):
        
        translation_tasks = get_list_or_404(TranslationTask, request_id=id)

        for task in translation_tasks:

            if task.status == "closed":
                return Response(None, status=status.HTTP_404_NOT_FOUND)

            if task.moderator != request.user:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)

            task.status = "closed"
            task.published = False
            task.save()

        return Response(None, status=status.HTTP_200_OK)


class TranslationUsersListView(ListAPIView):

    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_translator=True)
