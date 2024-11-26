from django.urls import path, include
from rest_framework.routers import DefaultRouter

from project.views import (
    SampleViewSet,
    AssemblyViewSet,
    ProjectViewSet,
    SequencingMethodViewSet,
    SequencingReadTypeViewSet,
    AssemblerViewSet,
    AnnotationViewSet,
    FileDownloadView
)

app_name = "project"

router = DefaultRouter()

router.register(r"project", ProjectViewSet, basename="project")
router.register(r"sample", SampleViewSet, basename="sample")
router.register(r"assembly", AssemblyViewSet, basename="assembly")

router.register(
    r"sequencing-method", SequencingMethodViewSet, basename="sequencing-method"
)
router.register(
    r"sequencing-read-type", SequencingReadTypeViewSet, basename="sequencing-read-type"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "project/<int:project_id>/samples/",
        SampleViewSet.as_view(actions={"get": "samples_by_project"}),
        name="samples-by-project",
    ),
    path(
        "project/<int:project_id>/assembly/",
        AssemblyViewSet.as_view(actions={"get": "assembly_by_project"}),
        name="assembly-by-project",
    ),
    path('download/<str:model_type>/<int:id>/',
         FileDownloadView.as_view(), name='download_file'),
    path('projects/<int:pk>/start_assembly/', AssemblerViewSet.as_view(
        actions={"post": "start_assembly"}), name='start-assembly'),
    path('projects/<int:pk>/start_annotation/', AnnotationViewSet.as_view(
        actions={"post": "start_annotation"}), name='start-annotation'),

]
