import re
import calendar
from datetime import datetime
from pathlib import Path

def reformat_date(file_name):
    date_formats = [
        (r'(\d{4})-(\d{1,2})-(\d{1,2})', '%Y-%m-%d'),  # YYYY-MM-DD
        (r'(\d{1,2})-(\d{1,2})-(\d{2})', '%m-%d-%y')   # MM-DD-YY
    ]
    for pattern, date_format in date_formats:
        if match := re.search(pattern, file_name):
            date = datetime.strptime(match.group(), date_format)
            return f"{date.year}-{date.month}-{date.day:02d}"
    return None

def rename_files(directory):
    path = Path(directory)
    for file_path in path.iterdir():
        if file_path.is_file():
            if new_date := reformat_date(file_path.name):
                new_name = re.sub(r'(\d{1,2}|\d{4})-(\d{1,2})-(\d{2}|\d{4})', new_date, file_path.name)
                file_path.rename(path / new_name)

# Example usage
rename_files(r"C:\Users\john1\Downloads\Outings_SingleExport\attempt 2\Outings_SingleExport files")
