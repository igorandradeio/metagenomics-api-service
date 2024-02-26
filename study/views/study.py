from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import status
import os
import shutil

from study.models import Study, Sample
from study.serializers import (
    StudySerializer,
    StudyDetailSerializer,
    SampleSerializer,
)


class StudyViewSet(ModelViewSet):

    queryset = Study.objects.all()

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return StudyDetailSerializer
        return StudySerializer


class SampleUploadViewSet(ViewSet):

    def create(self, request):
        serializer_class = SampleSerializer(data=request.data)

        if "file" not in request.FILES or not serializer_class.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            files = request.FILES.getlist("file")
            study = request.data.get("study")
            print(study)
            for file in files:
                handle_uploaded_file(file, study)

            return Response(status=status.HTTP_201_CREATED)


def handle_uploaded_file(file, study_id):
    base_dir = os.environ.get("UPLOAD_DIR")
    upload_dir = os.path.join(base_dir, str(study_id))

    # just for testing
    remove_directory(upload_dir)

    # Ensure the directory exists, if not, create it
    os.makedirs(upload_dir, exist_ok=True)

    # Build the complete path for the file
    file_path = os.path.join(upload_dir, file.name)

    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def remove_directory(directory):
    # Remove the entire directory
    try:
        shutil.rmtree(directory)
    except Exception as e:
        print(f"Error removing directory {directory}: {e}")
