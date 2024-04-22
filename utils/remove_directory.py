import shutil
import shutil
from project.models import Sample, Assembly


def remove_directory(directory, project_id):
    # Remove the entire directory
    try:
        shutil.rmtree(directory)
        samples_to_delete = Sample.objects.filter(project=project_id)
        assembly_to_delete = Assembly.objects.filter(project=project_id)

        if samples_to_delete.exists():
            samples_to_delete.delete()

        if assembly_to_delete.exists():
            assembly_to_delete.delete()
    except Exception as e:
        print(f"Error removing directory {directory}: {e}")
