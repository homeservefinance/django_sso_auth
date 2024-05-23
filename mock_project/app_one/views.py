from rest_framework.views import APIView
from rest_framework.response import Response

from mock_project.app_one.serializers import UserSerializer


class UserProfileView(APIView):
    """
    List all snippets, or create a new snippet.
    """

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
