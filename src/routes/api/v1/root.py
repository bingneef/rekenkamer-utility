from hashlib import md5

from flask import request, redirect, Blueprint
from src.models.source import Source

from src.util.logger import logger
from src.util.request import json_abort
from src.util.s3 import get_presigned_url, store_buffer_in_s3
from src.models.user import User
from src.util.zip import generate_zip_buffer
from src.util.app_engine import verify_access

api_v1_root = Blueprint("api_v1_root", __name__, url_prefix="/api/v1")


@api_v1_root.route("/private-document/<path:document_path>", methods=["GET"])
def get_custom_document(document_path):
    logger.info(f"Getting custom document {document_path}")

    if document_path[:14] == "source--custom":
        api_key = User.decode_document_access_token(request.values["access_token"])
        engine = document_path.split("/")[1]

        if not verify_access(api_key, f"source-custom-{engine}"):
            json_abort(401, "No access to the engine")

    document_url = get_presigned_url(document_path)

    return redirect(document_url)


@api_v1_root.route("/zip", methods=["POST"])
def download_zip():
    paths = request.form.getlist("document_paths")
    if len(paths) == 0:
        paths = request.json["document_paths"]

    custom_sources = Source.unique_custom_engines(paths)
    custom_sources = []
    if len(custom_sources) > 0:
        api_key = request.headers.get("X-Api-Key")

        for custom_source in custom_sources:
            if not verify_access(api_key, f"source-custom-{custom_source}"):
                json_abort(401, "No access to the engine")

    zip_io_buffer = generate_zip_buffer(paths)
    md5sum = md5(zip_io_buffer.getbuffer())

    path = store_buffer_in_s3(
        zip_io_buffer,
        bucket_name="private-artifacts",
        file_path=f"zip/{md5sum.hexdigest()}.zip",
    )
    url = get_presigned_url(path)

    return {"link": url}
