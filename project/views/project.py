from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from project.models import Project
from project.serializers import ProjectSerializer, ProjectDetailSerializer


class ProjectViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def list(self, request):
        user = request.user
        queryset = Project.objects.filter(user=user)
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)
