from rest_framework import serializers

from .models import Country, SequencingMethod, Project, Sample, SequencingReadType
from django.contrib.auth.models import User
import os


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class SequencingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMethod
        fields = "__all__"


class SequencingNestedMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMethod
        fields = ["id", "name"]


class SequencingReadTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingReadType
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    date = serializers.DateTimeField(
        source="created_at", read_only=True, format="%d-%m-%Y"
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "sequencing_method",
            "sequencing_read_type",
            "user",
            "date",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        project = Project.objects.create(user=user, **validated_data)
        return project


class SampleSerializer(serializers.ModelSerializer):
    file = serializers.FileField(max_length=None, allow_empty_file=False)

    class Meta:
        model = Sample
        fields = ["project", "file"]


class SampleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ["id", "project", "file"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    sequencing_method = SequencingNestedMethodSerializer()
    samples = SampleDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
