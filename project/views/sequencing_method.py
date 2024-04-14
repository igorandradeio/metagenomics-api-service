from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from project.models import SequencingMethod
from project.serializers import SequencingMethodSerializer


class SequencingMethodViewSet(ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = SequencingMethod.objects.all()
        serializer = SequencingMethodSerializer(queryset, many=True)
        return Response(serializer.data)
