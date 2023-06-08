from src.util.app_engine import (
    users_for_engine,
    update_elastic_engine_credentials,
    verify_access,
    api_key_for_email,
    create_engine,
    delete_engine,
)

from flask import Blueprint, request

from src.util.request import get_post_body, verify_body_keys, json_abort
from src.util.s3 import delete_custom_source_bucket

api_v1_engines = Blueprint("api_v1_engines", __name__, url_prefix="/api/v1/engines")


def verify_or_abort(engine: str) -> bool:
    api_key = request.headers.get("X-Api-Key")
    if verify_access(api_key, engine):
        return True

    json_abort(401, "No access to the engine")


def verify_or_abort_user(email: str) -> bool:
    api_key = request.headers.get("X-Api-Key")
    elastic_api_key = api_key_for_email(email)
    if elastic_api_key == api_key:
        return True

    json_abort(401, "Invalid credentials")


@api_v1_engines.route("", methods=["POST"])
def create_engine_for_user():
    body = get_post_body(request)

    verify_body_keys(body, ["engine", "email"])
    verify_or_abort_user(body["email"])

    create_engine(user_email=body["email"], engine=body["engine"])

    return {"acknowledged": True}


@api_v1_engines.route("/<engine>", methods=["DELETE"])
def remove_engine_route(engine):
    verify_or_abort(engine)

    api_search_key = request.headers.get("X-Api-Key")

    # TODO: delete all documents in correct order
    # delete_document_sources(engine)
    delete_custom_source_bucket(engine)
    delete_engine(engine, api_search_key)

    return {"acknowledged": True}


@api_v1_engines.route("/<engine>/users", methods=["GET"])
def engine_users(engine):
    verify_or_abort(engine)

    users = users_for_engine(engine)
    return users


@api_v1_engines.route("/<engine>/users", methods=["POST"])
def add_user_to_engine(engine):
    body = get_post_body(request)
    verify_body_keys(body, ["email"])

    verify_or_abort(engine)

    update_elastic_engine_credentials(email=body["email"], engines_to_add=[engine])

    return {"acknowledged": True}


@api_v1_engines.route("/<engine>/users/<email>", methods=["DELETE"])
def remove_user_to_engine(engine, email):
    verify_or_abort(engine)

    update_elastic_engine_credentials(email, engines_to_remove=[engine])

    return {"acknowledged": True}
