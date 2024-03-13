from rest_framework.serializers import (
    ModelSerializer,
    FileField,
    PrimaryKeyRelatedField,
)

from .models import Country, SequencingMethod, Project, Sample
from django.contrib.auth.models import User
import os


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class SequencingMethodSerializer(ModelSerializer):
    class Meta:
        model = SequencingMethod
        fields = "__all__"


class SequencingNestedMethodSerializer(ModelSerializer):
    class Meta:
        model = SequencingMethod
        fields = ["id", "name"]


class ProjectSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "sequencing_method", "sequencing_read_type", "user"]

    def create(self, validated_data):
        user = self.context["request"].user
        project = Project.objects.create(user=user, **validated_data)
        return project


class SampleSerializer(ModelSerializer):
    file = FileField(max_length=None, allow_empty_file=False)

    class Meta:
        model = Sample
        fields = ["project", "file"]


class SampleDetailSerializer(ModelSerializer):
    class Meta:
        model = Sample
        fields = ["id", "project", "file"]


class ProjectDetailSerializer(ModelSerializer):
    user = UserSerializer()
    sequencing_method = SequencingNestedMethodSerializer()
    samples = SampleDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
