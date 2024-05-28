from rest_framework import serializers
from .models import User


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class PasswordUpdateSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)

    def save(self, user):
        user.set_password(self.validated_data["password"])
        user.save()
        return user
