from src.models.source import Source
from src.models.user import User
from src.util.airflow import create_custom_source_job
from src.util.app_engine import verify_access, verify_format_and_uniqueness_name, create_engine, users_for_engine, \
    update_elastic_engine_credentials
from src.util.logger import logger
from src.util.request import json_abort, get_post_body, verify_body_keys
from flask import Blueprint, request

from src.util.s3 import base64_to_buffer, store_buffer_in_s3

api_v1_sources = Blueprint('api_v1_sources', __name__, url_prefix='/api/v1/sources')


@api_v1_sources.route('/', methods=['GET'])
def list_sources():
    sources = Source.list_sources()
    api_key = request.headers.get('X-Api-Key')
    custom_sources = []
    if api_key is not None and api_key != '-':
        custom_sources = Source.list_private_sources(api_key=api_key)

    return [*sources, *custom_sources]


@api_v1_sources.route('/', methods=['POST'])
def create_source():
    body = get_post_body(request)
    verify_body_keys(body, ['name', 'email'])

    engine_name = f"source-custom-{body['name']}"

    success, message = verify_format_and_uniqueness_name(engine_name=engine_name)
    if not success:
        json_abort(422, message)

    user = User.find_user(email=body['email'])

    if user is None or user.search_api_key != request.headers.get('X-Api-Key'):
        json_abort(401, "Invalid email or api key")

    logger.info(f"Creating custom source {engine_name} for user {user.email}")
    create_engine(engine=engine_name, user_email=user.email)
    return {'status': 'ok'}


@api_v1_sources.route('/<source_key>', methods=['GET'])
def get_source(source_key):
    # Check if the source is a custom source and if the user has access to it
    if source_key[:14] == 'source-custom-':
        api_key = request.headers.get('X-Api-Key')
        if api_key is None or not verify_access(api_key, f"source-custom-{source_key[14:]}"):
            json_abort(404, "Source not found")

        source = Source.get_source(source_key, fallback=True)
    else:
        source = Source.get_source(source_key)
        if source is None:
            json_abort(404, "Source not found")

    return source.clean_dict


@api_v1_sources.route('/<source_key>/documents', methods=['GET'])
def get_source_documents(source_key):
    fallback = False
    # Check if the source is a custom source and if the user has access to it
    if source_key[:14] == 'source-custom-':
        api_key = request.headers.get('X-Api-Key')
        if api_key is None or not verify_access(api_key, f"source-custom-{source_key[14:]}"):
            json_abort(404, "Source not found")
        fallback = True

    source = Source.get_source(source_key, fallback=fallback)
    if source is None:
        json_abort(404, "Source not found")

    if source_key[:14] != 'source-custom-':
        json_abort(404, "Can only show documents for custom source")

    api_key = request.headers.get('X-Api-Key')
    if api_key is None or not verify_access(api_key, f"source-custom-{source_key[14:]}"):
        json_abort(401, "No access to the engine")

    logger.info(f"Getting documents for {source_key}")
    return {
        'documents': source.list_documents()
    }


@api_v1_sources.route('/<source_key>/documents', methods=['POST'])
def create_source_documents(source_key):
    if source_key[:14] != 'source-custom-':
        json_abort(404, "Can only add documents for custom source")

    api_key = request.headers.get('X-Api-Key')
    if api_key is None or not verify_access(api_key, f"source-custom-{source_key[14:]}"):
        json_abort(401, "No access to the engine")

    body = get_post_body(request)
    verify_body_keys(body, ['documents'])

    for document in body['documents']:
        store_buffer_in_s3(
            buffer=base64_to_buffer(document['content']),
            bucket_name="source--custom",
            file_path=f"{source_key[14:]}/{document['filename']}"
        )

    create_custom_source_job(source=source_key[14:])

    return {
        'success': True
    }


@api_v1_sources.route('/<source_key>/documents/<filename>/', methods=['DELETE'])
def remove_source_document(source_key, filename):
    source = Source.get_source(source_key)
    if source is None:
        json_abort(404, "Source not found")

    if source_key[:14] != 'source-custom-':
        json_abort(404, "Can only remove documents for custom source")

    api_key = request.headers.get('X-Api-Key')
    if api_key is None or not verify_access(api_key, f"source-custom-{source_key[14:]}"):
        json_abort(401, "No access to the engine")

    logger.info(f"Removing document {filename}")
    success = source.delete_document(filename=filename, api_key=api_key)

    if not success:
        json_abort(500, "An error occurred")

    create_custom_source_job(source=source_key[14:])

    return {'success': success}


@api_v1_sources.route('/<source_key>/users', methods=['GET'])
def engine_users(source_key):
    if source_key[:14] != 'source-custom-':
        json_abort(404, "Can only get users for custom source")

    engine = f"source-custom-{source_key[14:]}"
    api_key = request.headers.get('X-Api-Key')
    if api_key is None or not verify_access(api_key, engine):
        json_abort(401, "No access to the engine")

    # TODO: This makes more requests than necessary, but it's fine for now
    users = [User.find_user(user_email).api_values for user_email in users_for_engine(engine)]
    return users


@api_v1_sources.route('/<source_key>/users', methods=['POST'])
def add_engine_users(source_key):
    if source_key[:14] != 'source-custom-':
        json_abort(404, "Can only add users for custom source")

    engine = f"source-custom-{source_key[14:]}"
    api_key = request.headers.get('X-Api-Key')
    if api_key is None or not verify_access(api_key, engine):
        json_abort(401, "No access to the engine")

    body = get_post_body(request)
    verify_body_keys(body, ['email'])

    update_elastic_engine_credentials(body['email'], engines_to_add=[engine])

    return {
        'acknowledged': True
    }


@api_v1_sources.route('/<source_key>/users/<email>', methods=['DELETE'])
def delete_engine_users(source_key, email):
    if source_key[:14] != 'source-custom-':
        json_abort(404, "Can only delete users for custom source")

    engine = f"source-custom-{source_key[14:]}"
    api_key = request.headers.get('X-Api-Key')
    if api_key is None or not verify_access(api_key, engine):
        json_abort(401, "No access to the engine")

    update_elastic_engine_credentials(email, engines_to_remove=[engine])

    return {
        'acknowledged': True
    }
