import zipfile
import io
from .s3 import get_document


def unique_custom_engines(paths) -> list[str]:
    custom_engines = set()
    for path in paths:
        if path[:14] == 'source--custom':
            custom_engines.add(path.split('/')[1])

    return list(custom_engines)


def generate_zip_buffer(paths: list[str], keep_folder_structure=False) -> io.BytesIO:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a",
                         zipfile.ZIP_DEFLATED, False) as zip_file:
        for path in paths:
            filename = path.split('/')[-1]
            result_folder_in_zip = f"documents/{filename}"
            if keep_folder_structure:
                result_folder_in_zip = f"documents/{path}"

            zip_file.writestr(result_folder_in_zip, get_document(path))

    zip_buffer.seek(0)
    return zip_buffer
