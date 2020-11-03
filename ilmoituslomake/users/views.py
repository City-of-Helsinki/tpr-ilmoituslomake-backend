from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from users.models import User
from users.serializers import UserSerializer

# Create your views here.
class UserView(RetrieveAPIView):
    """
    Returns the current user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
