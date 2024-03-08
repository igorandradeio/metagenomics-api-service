from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]

    username = serializers.CharField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
