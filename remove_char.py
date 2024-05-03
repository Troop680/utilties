from pathlib import Path
import re

def sanitize_filename(file_path):
    # Define a pattern to match characters not allowed in zip filenames
    pattern = r'[\/:*?"<>|’–]'

    # Replace these characters with an underscore or remove them
    sanitized_name = re.sub(pattern, '_', file_path.name)

    return sanitized_name

def sanitize_files(directory):
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_file():
            new_name = sanitize_filename(file_path)
            if new_name != file_path.name:
                new_file_path = file_path.with_name(new_name)
                file_path.rename(new_file_path)

# Example usage
sanitize_files(r"C:\Users\john1\Downloads\Outings_SingleExport\attempt 2\Outings_SingleExport files")
