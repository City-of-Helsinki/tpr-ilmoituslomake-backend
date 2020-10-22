from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView


class HelloView(RetrieveAPIView):
    """
    A view that returns Hello! message in JSON.
    """

    renderer_classes = [JSONRenderer]

    def get(self, request, format=None):
        content = {"message": "Hello world!"}
        return Response(content)
