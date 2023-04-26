from src.util.app_engine import verify_access
from flask import Blueprint, request

from src.util.logger import logger
from src.util.request import json_abort
from src.util.s3 import get_presigned_url

api_v1_private_documents = Blueprint('api_v1_private_documents', __name__, url_prefix='/api/v1/private-documents')


@api_v1_private_documents.route('/<path:document_path>', methods=['GET'])
def get_custom_document(document_path):
    logger.info(f"Getting custom document {document_path}")

    if document_path[:14] == 'source--custom':
        api_key = request.headers.get('X-Api-Key')
        engine = document_path.split('/')[1]

        if not verify_access(api_key, f"source-custom-{engine}"):
            json_abort(401, "No access to the engine")

    document_url = get_presigned_url(document_path)

    return {"url": document_url}
