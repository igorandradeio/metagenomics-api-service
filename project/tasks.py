from __future__ import absolute_import, unicode_literals

from celery import shared_task
import subprocess
import os
from utils.remove_directory import remove_assembly_directory


@shared_task
def run_megahit(project_id, sequencing_read_type, input_files):
    """
    Run MEGAHIT based on the sequencing read type.

    Parameters:
    - project_id (int): ID of the project for which the MEGAHIT assembly is being run.
    - sequencing_read_type (int): Sequencing type (1 for single-end, 2 for paired-end).
    - input_files (list): List of input files. For single-end, it will be a list with one file. For paired-end, it will be a list with two files.
    """

    # Define output directory
    base_dir = os.environ.get("UPLOAD_DIR")
    output_dir = os.path.join(base_dir, str(project_id), "assembly")

    # Delete the last output directory
    remove_assembly_directory(output_dir, project_id)

    # Construct the MEGAHIT command based on the sequencing read type
    if sequencing_read_type == 1:
        cmd = ["megahit", "-r", input_files[0], "-o", output_dir]
    elif sequencing_read_type == 2:
        cmd = ["megahit", "-1", input_files[0], "-2", input_files[1], "-o", output_dir]
    else:
        raise ValueError(
            "Invalid sequencing read type. Use 1 for single-end or 2 for paired-end."
        )
    # Execute the command
    result = subprocess.run(cmd, capture_output=True, text=True)

    return result.stdout, result.stderr
