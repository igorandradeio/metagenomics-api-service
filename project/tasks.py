from __future__ import absolute_import, unicode_literals

from celery import shared_task
import subprocess
import os
from django.conf import settings
from utils.remove_directory import remove_assembly_directory
from utils.remove_work_dir import remove_work_dir
from task.models import Task, TaskStatus
from user.models import User
from project.models import Assembly, Project
import logging
import csv

# Define constants for sequencing read types
SINGLE_END = 1
PAIRED_END = 2


@shared_task(bind=True)
def run_megahit(self, project_id, sequencing_read_type, input_files, user_id, options):
    """
    Execute Nextflow pipeline to run MEGAHIT.

    Parameters:
    - project_id (int): ID of the project for which the assembly is being run.
    - sequencing_read_type (int): Sequencing type (1 for single-end, 2 for paired-end).
    - input_files (list): List of input files (one for single-end, two for paired-end).
    - user_id (int): ID of the user who initiated the task.
    """

    task_id = self.request.id
    user = User.objects.get(id=user_id)
    project = Project.objects.get(id=project_id)
    k_count, k_min, k_max, k_step = options
    current_dir = os.path.join(
        "media", "projects", str(project_id), "assembly")
    output_dir = os.path.join("media", "projects", str(project_id))

    # Remove previous assembly directory if it exists
    remove_assembly_directory(current_dir, project_id)

    # Update task status to "STARTED"
    save_task_status(user, task_id, project, TaskStatus.STARTED)

    workflow_path = os.path.join(
        settings.BASE_DIR, 'nextflow', 'workflows', 'megahit', 'main.nf')
    work_dir = os.path.join(settings.BASE_DIR, 'nextflow',
                            'workflows', 'megahit', task_id)

    # Build the Nextflow command
    nextflow_command = [
        "nextflow", "run", workflow_path,
        "-with-conda",
        "-work-dir", work_dir,
        "--output", output_dir,
        "--read_type", str(sequencing_read_type),
        "--k_count", str(k_count),
        "--k_min", str(k_min),
        "--k_max", str(k_max),
        "--k_step", str(k_step),
    ]

    # Construct the MEGAHIT command based on the sequencing read type
    if sequencing_read_type == SINGLE_END:
        nextflow_command.extend(["--read1", input_files[0]])

    elif sequencing_read_type == PAIRED_END:
        nextflow_command.extend(
            ["--read1", input_files[0], "--read2", input_files[1]])
    else:
        error_msg = (
            "Invalid sequencing read type. Use 1 for single-end or 2 for paired-end."
        )
        # Sets the task status to "FAILURE"
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        raise ValueError(error_msg)
    try:
        result = subprocess.run(
            nextflow_command, capture_output=True, text=True, check=True)

        # On success, update task status
        save_task_status(user, task_id, project, TaskStatus.SUCCESS)

        file_name = os.environ.get("FINAL_CONTIGS_NAME")
        file_path = os.path.join(current_dir, file_name)

        assembly = Assembly(
            file_name=file_name,
            project=project,
            file=file_path.replace("media/", ""),
            upload_source=1
        )
        assembly.save()
        remove_work_dir(work_dir)

        return result.stdout, result.stderr

    except subprocess.CalledProcessError as e:
        error_msg = f"Nextflow pipeline failed with return code {e.returncode}: {e.stderr}"
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        remove_work_dir(work_dir)

        return error_msg

    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        save_task_status(user, task_id, project, TaskStatus.FAILURE, error_msg)
        remove_work_dir(work_dir)

        return error_msg


@shared_task(bind=True)
def run_analysis(self, project_id, sequencing_read_type, input_files, user_id):

    task_id = self.request.id
    user = User.objects.get(id=user_id)
    project = Project.objects.get(id=project_id)
    current_dir = os.path.join(
        "media", "projects", str(project_id), "assembly")
    output_dir = os.path.join("media", "projects", str(project_id))

    # Update task status to "STARTED"
    save_task_status(user, task_id, project, TaskStatus.STARTED)

    # Construct file paths
    sample_dir = os.path.join("media", "projects", str(project_id), "sample")

    # Construct the file paths
    file_paths = [
        os.path.join(sample_dir, file_name) for file_name in input_files
    ]

    # Generate the CSV file
    csv_file_path = os.path.join(sample_dir, "samplesheet.csv")
    with open(csv_file_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # Write the header
        writer.writerow(["sample", "group", "short_reads_1",
                        "short_reads_2", "long_reads"])
        # Write the data
        writer.writerow(
            [f"sample_1", "0", file_paths[0], file_paths[1], ""])

    # Construct the Nextflow command
    nextflow_command = [
        "nextflow", "run", "nf-core/mag",
        "-r", "3.2.1",
        "--skip_spades", "--skip_spadeshybrid", "--skip_quast", "--skip_binning",
        "-profile", "test,apptainer",
        "--outdir", output_dir,
    ]

    try:
        result = subprocess.run(
            nextflow_command, capture_output=True, text=True, check=True)

        # On success, update task status
        save_task_status(user, task_id, project, TaskStatus.SUCCESS)

        return result.stdout, result.stderr

    except subprocess.CalledProcessError as e:
        error_msg = f"Nextflow pipeline failed with return code {e.returncode}: {e.stderr}"
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
    - project: The project object.
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
        logger.error(
            f"Task with ID {task_id} does not exist. Unable to update status.")

    except Exception as e:
        logger.error(f"Failed to update task with ID {task_id}: {str(e)}")

    if error_msg:
        logger.error(error_msg)
