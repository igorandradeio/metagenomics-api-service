from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True, format="%d-%m-%Y %H:%M:%S")
    updated_at = serializers.DateTimeField(read_only=True, format="%d-%m-%Y %H:%M:%S")
    class Meta:
        model = Task
        fields = ["id", "user", "task_id" ,"type", "type_name" ,"project", "status", "status_name", "created_at", "updated_at"]

    def get_type_name(self, obj):
        return obj.get_type_display()

    def get_status_name(self, obj):
        return obj.get_status_display()