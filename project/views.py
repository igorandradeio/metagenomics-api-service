from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ViewSet):
    """
    Viewset for viewing all projects
    """

    queryset = Project.objects.all()

    def list(self, request):
        serializer = ProjectSerializer(self.queryset, many=True)

        return Response(serializer.data)
