from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from authentication.serializers import UserSerializer


@api_view(["POST"])
def login(request):
    if "email" not in request.data or "password" not in request.data:
        return Response(
            "Both e-mail and password are required",
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(email=request.data["email"]).first()

    if not user:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

    if not user.check_password(request.data["password"]):
        return Response("Incorrect password", status=status.HTTP_401_UNAUTHORIZED)

    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    auth_token = request.auth
    if auth_token:
        request.user.auth_token.delete()
    return Response({"logout": "success"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)
