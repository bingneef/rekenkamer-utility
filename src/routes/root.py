import os

import requests
from flask import send_file, request, redirect, Blueprint

from src.util.db import get_conn
from src.util.logger import logger
from src.util.request import json_abort
from src.util.s3 import get_presigned_url
from src.models.user import User
from src.util.zip import generate_zip_buffer, unique_custom_engines
from src.util.app_engine import verify_access

root = Blueprint('root', __name__, url_prefix='/')


@root.route('/')
def landing():
    return "Welcome to the utility API"


@root.route('/healthcheck')
def healthcheck():
    # Verify DB is working
    get_conn()['users'].find({}).limit(1)

    return {
        'status': 'ok'
    }


@root.route('/private-document/<path:document_path>', methods=['GET'])
def get_custom_document(document_path):
    logger.info(f"Getting custom document {document_path}")

    if document_path[:14] == 'source--custom':
        api_key = User.decode_document_access_token(request.values['access_token'])
        engine = document_path.split('/')[1]

        if not verify_access(api_key, f"source-custom-{engine}"):
            json_abort(401, "No access to the engine")

    document_url = get_presigned_url(document_path)

    return redirect(document_url)


@root.route('/zip', methods=['POST'])
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
            if not verify_access(api_key, f"source-custom-{custom_source}"):
                json_abort(401, "No access to the engine")

    zip_io_buffer = generate_zip_buffer(paths, keep_folder_structure)

    return send_file(
        zip_io_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )
