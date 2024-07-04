from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField()
    status_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ["id", "user", "task_id" ,"type", "type_name" ,"project", "status", "status_name"]

    def get_type_name(self, obj):
        return obj.get_type_display()

    def get_status_name(self, obj):
        return obj.get_status_display()