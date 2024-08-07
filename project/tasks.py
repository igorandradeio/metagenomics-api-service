from __future__ import absolute_import, unicode_literals

from celery import shared_task
import subprocess
import os
from utils.remove_directory import remove_assembly_directory
from task.models import Task, TaskStatus
from user.models import User
from project.models import Assembly, Project

# Define constants for sequencing read types
SINGLE_END = 1
PAIRED_END = 2


@shared_task(bind=True)
def run_megahit(self, project_id, sequencing_read_type, input_files, user_id, options):
    """
    Run MEGAHIT based on the sequencing read type.

    Parameters:
    - project_id (int): ID of the project for which the MEGAHIT assembly is being run.
    - sequencing_read_type (int): Sequencing type (1 for single-end, 2 for paired-end).
    - input_files (list): List of input files. For single-end, it will be a list with one file. For paired-end, it will be a list with two files.
    - user_id (int): ID of the user who initiated the task.
    """
    task_id = self.request.id
    user = User.objects.get(id=user_id)
    project = Project.objects.get(id=project_id)
    k_count, k_min, k_max, k_step = options



    # Save the initial status as pending
    save_task_status(user, task_id, project, TaskStatus.STARTED)

    base_dir = os.environ.get("UPLOAD_DIR")
    output_dir = os.path.join(base_dir, str(project_id), "assembly")

    # Delete the last output directory
    remove_assembly_directory(output_dir, project_id)

    command = [
        "megahit",
        "-o", output_dir,
        "--min-count", str(k_count),
        "--k-min", str(k_min),
        "--k-max", str(k_max),
        "--k-step", str(k_step)
    ]
    
    # Construct the MEGAHIT command based on the sequencing read type
    if sequencing_read_type == SINGLE_END:
        command.extend(["-r", input_files[0]])

    elif sequencing_read_type == PAIRED_END:
        command.extend(["-1", input_files[0], "-2", input_files[1]])
    else:
        error_msg = (
            "Invalid sequencing read type. Use 1 for single-end or 2 for paired-end."
        )
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        raise ValueError(error_msg)

    try:
        # Execute the command with check=True
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        save_task_status(user, task_id, project, TaskStatus.SUCCESS)
        file_name = "final.contigs.fa"
        assembly = Assembly(
            file_name=file_name,
            project=project,
            file=f"{output_dir}/{file_name}",
            upload_source=1
        )
        assembly.save()

        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        error_msg = (
            f"MEGAHIT command failed with return code {e.returncode}: {e.stderr}"
        )
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        return error_msg


def save_task_status(user, task_id, project, status, error_msg=None):
    """
    Save or update the status of a task in the database.

    Parameters:
    - user (User): The user object.
    - task_id (str): The ID of the Celery task.
    - status (int): The status code of the task (1 for pending, 2 for success, 3 for failure).
    - error_msg (str, optional): The error message if the task failed.
    """
    task, created = Task.objects.get_or_create(
        user=user, task_id=task_id, defaults={"type": 1, "project": project, "status": status}
    )
    if not created:
        task.status = status
        task.save()
    if error_msg:
        # Log the error message or handle it as needed
        print(error_msg)
