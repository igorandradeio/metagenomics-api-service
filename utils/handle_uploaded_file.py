import os


def handle_uploaded_file(file, project_id, upload_dir):
    try:
        # Build the complete path for the file
        file_path = os.path.join(upload_dir, file.name)

        with open(file_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        return file_path
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return None
