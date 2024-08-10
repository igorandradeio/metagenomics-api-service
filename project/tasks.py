from __future__ import absolute_import, unicode_literals

from celery import shared_task
import subprocess
import os
from utils.remove_directory import remove_assembly_directory
from task.models import Task, TaskStatus
from user.models import User
from project.models import Assembly, Project
import logging

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
    base_dir = os.environ.get("UPLOAD_DIR")
    output_dir = os.path.join(base_dir, str(project_id), "assembly")
    # Delete the last output directory
    remove_assembly_directory(output_dir, project_id)
    
    # Sets the task status to "STARTED"
    save_task_status(user, task_id, project, TaskStatus.STARTED)

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
        # Sets the task status to "FAILURE"
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        raise ValueError(error_msg)

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Sets the task status to "SUCCESS"
        save_task_status(user, task_id, project, TaskStatus.SUCCESS)
        file_name = os.environ.get("FINAL_CONTIGS_NAME")

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
    Update the status of a task in the database.

    Parameters:
    - user (User): The user object.
    - task_id (str): The ID of the Celery task.
    - status (int): The status code of the task (1 for pending, 2 for success, 3 for failure).
    - error_msg (str, optional): The error message if the task failed.
    """
    logger = logging.getLogger(__name__)

    try:
        # Attempt to get the existing task
        task = Task.objects.get(
            user=user,
            task_id=task_id,
            type=1,
            project=project
        )
        # Update the existing task's status
        task.status = status
        task.save()

    except Task.DoesNotExist:
        logger.error(f"Task with ID {task_id} does not exist. Unable to update status.")

    except Exception as e:
        logger.error(f"Failed to update task with ID {task_id}: {str(e)}")

    if error_msg:
        logger.error(error_msg)