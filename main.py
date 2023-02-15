from flask import Flask, send_file, request, abort, redirect
from app.util.log import logging
from app.models.user import User
from app.util.zip import generate_zip_buffer, unique_custom_engines
from app.util.s3 import get_presigned_url
from app.util.app_engine import verify_access

app = Flask(__name__)


@app.route('/healthcheck')
def healthcheck():
    return {
        'status': 'ok'
    }


@app.route('/auth/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.find_user(email)
    if user is None:
        logging.info("User not found, invalid email")
        abort(401, description="Invalid credentials")

    if not user.verify_password(password):
        logging.info("User not found, invalid password")
        abort(401, description="Invalid credentials")

    return {
        'display_name': user.display_name,
        'search_api_key': user.search_api_key_fmt,
        'document_access_token': user.document_access_token
    }


@app.route('/private-document/<path:document_path>', methods=['GET'])
def get_custom_document(document_path):
    print(f"Getting custom document {document_path}")

    if document_path[:14] == 'source--custom':
        api_key = User.decode_document_access_token(request.values['access_token'])
        engine = document_path.split('/')[1]

        if not verify_access(api_key, engine):
            raise Exception('No access to engine')

    document_url = get_presigned_url(document_path)

    return redirect(document_url)


@app.route('/zip', methods=['POST'])
def download_zip():
    paths = request.form.getlist('document_paths[]')
    keep_folder_structure = int(request.form.get('keep_folder_structure', 0)) == 1
    filename = request.form.get('filename', 'results.zip')

    if filename[-4:] != '.zip':
        filename = f"{filename}.zip"

    custom_sources = unique_custom_engines(paths)
    if len(custom_sources) > 0:
        api_key = User.decode_document_access_token(request.values['access_token'])

        for custom_source in custom_sources:
            if not verify_access(api_key, custom_source):
                raise Exception('No access to engine')

    zip_io_buffer = generate_zip_buffer(paths, keep_folder_structure)

    return send_file(
        zip_io_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=5000)
