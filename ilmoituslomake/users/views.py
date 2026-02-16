from rest_framework.permissions import IsAuthenticated
# 10.4.2025 jlasanen
from helusers.oidc import ApiTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import logout

from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from users.models import User
from users.serializers import UserSerializer

# Create your views here.
class UserView(RetrieveAPIView):
    """
    Returns the current user
    """

    # 10.4.2025 jlasanen
    authentication_classes = [ApiTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class UserLogout(APIView):
    """
    Logout the user
    """

    def get(self, request, format=None):
        # using Django logout
        logout(request)
        return Response(status=status.HTTP_200_OK)
