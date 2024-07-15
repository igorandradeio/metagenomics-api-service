from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from task.models import Task
from task.serializers import TaskSerializer


class TaskViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        queryset = Task.objects.filter(user=user).order_by('-id')
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)