from flask import Flask, send_file, request
import zipfile
import io
from util.s3 import get_document

app = Flask(__name__)


def generate_zip(paths: list[str], keep_folder_structure=False) -> io.BytesIO:
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


@app.route('/zip', methods=['POST'])
def download_zip():
    paths = request.form.getlist('document_paths[]')
    keep_folder_structure = int(request.form.get('keep_folder_structure', 0)) == 1
    filename = request.form.get('filename', 'results.zip')

    if filename[-4:] != '.zip':
        filename = f"{filename}.zip"

    zip_io_buffer = generate_zip(paths, keep_folder_structure)

    return send_file(
        zip_io_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=5000)
