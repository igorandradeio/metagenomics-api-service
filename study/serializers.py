from rest_framework.serializers import ModelSerializer, FileField

from .models import Country, SequencingMethod, Study, Sample
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


class StudySerializer(ModelSerializer):
    class Meta:
        model = Study
        fields = "__all__"


class StudyDetailSerializer(ModelSerializer):
    user = UserSerializer()
    sequencing_method = SequencingNestedMethodSerializer()

    class Meta:
        model = Study
        fields = "__all__"
        depth = 1


class SampleSerializer(ModelSerializer):
    file = FileField(max_length=None, allow_empty_file=False)

    class Meta:
        model = Sample
        fields = ["study", "file"]
