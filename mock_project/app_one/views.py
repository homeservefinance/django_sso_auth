from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from django_sso_auth.drf.permissions import IsMemberOfGroup


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsMemberOfGroup]
    required_group = "hs_admin"

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({"username": user.username, "email": user.email})
