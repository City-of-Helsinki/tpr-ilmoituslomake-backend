from copy import error
import json
from translation.serializers import TranslationTaskWithDataSerializer, TranslationTaskSerializer, ChangeRequestSerializer, TranslationRequestSerializer
from translation.models import TranslationTask
from django.shortcuts import get_object_or_404, render
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView
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

        request_id = 1
        new_request_id = 1
        if len(TranslationTask.objects.all()) > 0:
            new_request_id = TranslationTask.objects.all().order_by("-request_id")[0].request_id + 1

        headers = None      
        # Creates a new translation task entry 
        # for every target in the request
        request_data = request.data.copy()
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

    # def post(self, request, *args, **kwargs):
    #     return self.create(request, *args, **kwargs)


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


class TranslationTaskRetrieveView(RetrieveAPIView):
    lookup_field = "id"
    queryset = TranslationTask.objects.all()
    serializer_class = TranslationTaskWithDataSerializer

    def get(self, request, id=None, *args, **kwargs):  
        '''
        Returns all translation task objects with some id
        '''      
        translation_task = get_object_or_404(TranslationTask, id=id)
        serializer = TranslationTaskWithDataSerializer(
            translation_task, context={"id": id}
        )
        ret = serializer.data
        target = serializer.data["target"]["data"]
        
        # TODO: Figure out how data works.

        return Response(ret, status=status.HTTP_200_OK)


class TranslationRequestRetrieveView(RetrieveAPIView):

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
            "status": first_task["status"],
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
                }
            }
            base["tasks"].append(single_task)

        
        return Response(base, status=status.HTTP_200_OK)


class TranslationTaskSearchListView(ListAPIView):
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

    # Creates a queryset of TranslationTasks with unique request_ids i.e. 
    # always the first TranslationTask of the request.
    # values_list = TranslationTask.objects.values_list('request_id', 'id').distinct()
    # ids_list = []
    # requirement_id_list = [] 
    # for value in values_list:
    #     if value[0] not in requirement_id_list:
    #         ids_list.append(value[1])
    #         requirement_id_list.append(value[0])

    # queryset = TranslationTask.objects.filter(pk__in=ids_list)
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
