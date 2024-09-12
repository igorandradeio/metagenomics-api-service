import os
import subprocess

def remove_work_dir(work_dir):
    """Helper function to remove the work directory if it exists."""
    if os.path.exists(work_dir):
        subprocess.run(["rm", "-rf", work_dir])