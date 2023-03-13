import os

from src.util.app_engine import update_elastic_engine_credentials
from src.util.auth import get_verification_code
from src.util.request import get_post_body, verify_body_keys, json_abort
from src.models.user import User
from flask import request

import logging

from flask import Blueprint

api_v1_auth = Blueprint('api_v1_auth', __name__, url_prefix='/api/v1/auth')


@api_v1_auth.route('/login', methods=['POST'])
def login():
    body = get_post_body(request)
    verify_body_keys(body, ['email', 'password'])

    email = body['email']
    password = body['password']

    user = User.find_user(email)
    if user is None:
        logging.info("User not found, invalid email")
        json_abort(401, "Invalid credentials")

    if not user.verify_password(password):
        logging.info("User not found, invalid password")
        json_abort(401, "Invalid credentials")

    return {
        'display_name': user.display_name,
        'search_api_key': user.search_api_key,
        'document_access_token': user.document_access_token
    }


@api_v1_auth.route('/signup', methods=['POST'])
def signup_route():
    body = get_post_body(request)
    verify_body_keys(body, ['display_name', 'email', 'password', 'verification_code'])

    if body['verification_code'] != get_verification_code(body['email']):
        logging.info("Invalid verification code")
        json_abort(401, "Invalid verification code")

    user = User.find_user(email=body['email'])
    if user is not None:
        logging.info("User already exists")
        json_abort(422, "User already exists")

    user = User(
        display_name=body['display_name'],
        email=body['email'],
        password=body['password']
    )
    user.persist()

    print(f"Created user: {user}")

    return {
        'display_name': user.display_name,
        'search_api_key': user.search_api_key,
        'document_access_token': user.document_access_token
    }


@api_v1_auth.route('/update-engine-credentials', methods=['PUT'])
def update_engine_credentials():
    if request.headers.get('X-Auth-Token') != os.environ['AUTH_TOKEN']:
        json_abort(401, "Invalid auth token")

    body = get_post_body(request)
    verify_body_keys(body, ['email', 'engines_to_add', 'engines_to_remove'])

    engines = update_elastic_engine_credentials(
        email=body['email'],
        engines_to_add=body['engines_to_add'],
        engines_to_remove=body['engines_to_remove']
    )

    return {
        'engines': engines
    }
