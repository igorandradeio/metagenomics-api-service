from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import os
from utils.handle_uploaded_file import handle_uploaded_file
from utils.remove_directory import remove_sample_directory

from project.models import Project, Sample
from project.serializers import SampleListSerializer, SamplePairSerializer
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from collections import defaultdict


class SampleViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def samples_by_project(self, request, project_id):
        # Get the project object and check if it exists
        project = get_object_or_404(Project, pk=project_id, user=request.user)

        # Get the sequencing_read_type_id value from the project
        sequencing_read_type_id = project.sequencing_read_type_id

        # Filter samples related to the project
        samples = Sample.objects.filter(project=project)

        if samples.exists():
            if sequencing_read_type_id == 2:
                # Current flow: group by pair_id
                grouped_samples = defaultdict(list)
                for sample in samples:
                    grouped_samples[sample.pair_id].append(sample)

                paired_samples = []
                for sample_pair in grouped_samples.values():
                    paired_samples.append({
                        "pair_id": sample_pair[0].pair_id,
                        "samples": sample_pair
                    })

                # Serialize the grouped samples and return them
                serializer = SamplePairSerializer(paired_samples, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

            elif sequencing_read_type_id == 1:
                # New flow: pair_id is null and keep samples in their own array
                paired_samples = []
                for sample in samples:
                    paired_samples.append({
                        "pair_id": None,
                        "samples": [sample]
                    })

                # Serialize the new format and return the data
                serializer = SamplePairSerializer(paired_samples, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # If no samples are found
            return Response({"error": "No samples found for this project."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        if "r1" in request.FILES and "r2" in request.FILES:
            r1 = request.FILES["r1"]
            r2 = request.FILES["r2"]

            project_id = request.data.get("project")
            project = get_object_or_404(
                Project, pk=project_id, user=request.user)

            last_pair = project.samples.order_by("-pair_id").first()
            next_pair_id = (last_pair.pair_id + 1) if last_pair else 1

            upload_dir = os.path.join(
                "media", "projects", str(project_id), "sample")

            # remove_sample_directory(upload_dir, project_id)
            os.makedirs(upload_dir, exist_ok=True)

            r1_saved = handle_uploaded_file(r1, project_id, upload_dir)
            r2_saved = handle_uploaded_file(r2, project_id, upload_dir)

            if r1_saved and r2_saved:
                sample1 = Sample(
                    file_name=r1.name,
                    project=project,
                    file=r1_saved.replace("media/", ""),
                    read_orientation=1,
                    pair_id=next_pair_id,
                )
                sample1.save()

                sample2 = Sample(
                    file_name=r2.name,
                    project=project,
                    file=r2_saved.replace("media/", ""),
                    read_orientation=2,
                    pair_id=next_pair_id,
                )
                sample2.save()

            return Response(status=status.HTTP_201_CREATED)

        elif "file" in request.FILES:
            file = request.FILES["file"]

            project_id = request.data.get("project")
            project = get_object_or_404(
                Project, pk=project_id, user=request.user)

            upload_dir = os.path.join(
                "media", "projects", str(project_id), "sample")

            # remove_sample_directory(upload_dir, project_id)
            os.makedirs(upload_dir, exist_ok=True)

            file_saved = handle_uploaded_file(file, project_id, upload_dir)

            if file_saved:
                sample = Sample(
                    file_name=file.name,
                    project=project,
                    file=file_saved.replace("media/", ""),
                )
                sample.save()

            return Response(status=status.HTTP_201_CREATED)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
