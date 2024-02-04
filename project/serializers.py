from rest_framework import serializers

from .models import Country, SequencingMethod, Project, File


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class SequencingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = SequencingMethod
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"
