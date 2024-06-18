from __future__ import absolute_import, unicode_literals

from celery import shared_task
import subprocess
import os
from utils.remove_directory import remove_assembly_directory
from project.models import Task
from user.models import User

# Define constants for sequencing read types
SINGLE_END = 1
PAIRED_END = 2


@shared_task
def run_megahit(project_id, sequencing_read_type, input_files, user_id):
    """
    Run MEGAHIT based on the sequencing read type.

    Parameters:
    - project_id (int): ID of the project for which the MEGAHIT assembly is being run.
    - sequencing_read_type (int): Sequencing type (1 for single-end, 2 for paired-end).
    - input_files (list): List of input files. For single-end, it will be a list with one file. For paired-end, it will be a list with two files.
    - user_id (int): ID of the user who initiated the task.
    """

    user = User.objects.get(id=user_id)
    base_dir = os.environ.get("UPLOAD_DIR")
    output_dir = os.path.join(base_dir, str(project_id), "assembly")

    # Delete the last output directory
    remove_assembly_directory(output_dir, project_id)

    # Construct the MEGAHIT command based on the sequencing read type
    if sequencing_read_type == SINGLE_END:
        cmd = ["megahit", "-r", input_files[0], "-o", output_dir]
    elif sequencing_read_type == PAIRED_END:
        cmd = ["megahit", "-1", input_files[0], "-2", input_files[1], "-o", output_dir]
    else:
        error_msg = (
            "Invalid sequencing read type. Use 1 for single-end or 2 for paired-end."
        )
        save_task_status(user, 3, error_msg)
        raise ValueError(error_msg)

    try:
        # Execute the command with check=True
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        save_task_status(user, 2)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        error_msg = (
            f"MEGAHIT command failed with return code {e.returncode}: {e.stderr}"
        )
        save_task_status(user, 3, error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        save_task_status(user, 3, error_msg)
        return error_msg


def save_task_status(user, status, error_msg=None):
    """
    Save the status of a task to the database.

    Parameters:
    - user (User): The user object.
    - status (int): The status code of the task (2 for success, 3 for failure).
    - error_msg (str, optional): The error message if the task failed.
    """
    task = Task(user=user, status=status)
    task.save()
    if error_msg:
        # Log the error message or handle it as needed
        print(error_msg)
