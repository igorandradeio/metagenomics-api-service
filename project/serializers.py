from rest_framework import serializers

from .models import Country, SequencingMethod, Project, Sample, Assembly, SequencingReadType
from user.models import User
import os


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class SequencingMethodSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source="id")
    label = serializers.CharField(source="name")

    class Meta:
        model = SequencingMethod
        fields = ["value", "label"]


class SequencingNestedMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMethod
        fields = ["id", "name"]


class SequencingReadTypeSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(source="id")
    label = serializers.CharField(source="name")

    class Meta:
        model = SequencingReadType
        fields = ["value", "label"]


class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    date = serializers.DateTimeField(
        source="created_at", read_only=True, format="%d-%m-%Y"
    )
    sample_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "sequencing_method",
            "sequencing_read_type",
            "user",
            "date",
            "sample_count",
        ]

    def get_sample_count(self, obj):
        return obj.samples.count()

    def create(self, validated_data):
        user = self.context["request"].user
        project = Project.objects.create(user=user, **validated_data)
        return project


class SampleListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        source="created_at", read_only=True, format="%d-%m-%Y"
    )
    download = serializers.SerializerMethodField()

    class Meta:
        model = Sample
        fields = ["id", "project_id", "file_name", "download", "date"]

    def get_download(self, obj):
        base_url = os.environ.get("BASE_URL")
        return f"{base_url}/api/samples/{obj.pk}/download/"


class AssemblyListSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        source="created_at", read_only=True, format="%d-%m-%Y"
    )
    download = serializers.SerializerMethodField()

    class Meta:
        model = Assembly
        fields = ["id", "project_id", "file_name", "download", "date", "upload_source"]

    def get_download(self, obj):
        base_url = os.environ.get("BASE_URL")
        return f"{base_url}/api/assembly/{obj.pk}/download/"


class AssemblySerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False)

    class Meta:
        model = Sample
        fields = ["project", "file"]


class SampleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ["id", "project", "file"]


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ["id", "file"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    samples = SampleDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

class StartTaskSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=True)
