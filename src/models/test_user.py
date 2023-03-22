import pytest
import time_machine

from .user import User

default_args = {
    "_id": "123",
    "display_name": 'AR',
    "email": 'info@example.com',
    "password": 'testtest'
}


def test_post_init():
    user = User(**default_args)
    assert user.password is None, "Password should be None"

    assert user.password_hash is not None, "Password hash should be None"
    assert user.search_api_key_hash is not None, "SearchApiKey hash should be None"


def test_clean_dict():
    user = User(**default_args)

    expected_keys = ['display_name', 'email', 'password_hash', 'salt', 'search_api_key_hash', 'search_api_key_name']

    assert set(user.clean_dict.keys()) == set(expected_keys), "Clean dict should only contain these keys"


def test_verify_password():
    user = User(**default_args)

    assert user.verify_password('testtest'), "Password should be verified"


def test_unique_salt():
    user = User(**default_args)
    user2 = User(**{**default_args, 'email': 'noreply@example.com'})

    assert user.salt != user2.salt, "Salt should be unique"


def test_search_api_key():
    user = User(**default_args)

    assert user.search_api_key == 'private-123', "SearchApiKey should be formatted correctly"


def test_search_api_key_check_email():
    user = User(**default_args)
    user.email = 'noreply@example.com'

    with pytest.raises(Exception):
        user.search_api_key


def test_document_access_token():
    user = User(**default_args)

    with time_machine.travel('2021-01-01 00:00:00'):
        token = user.document_access_token

    with time_machine.travel('2021-01-01 23:59:59'):
        assert user.decode_document_access_token(
            token) == 'private-123', "Document access token should be decoded correctly"


def test_document_access_token_expired():
    user = User(**default_args)

    with time_machine.travel('2021-01-01 00:00:00'):
        token = user.document_access_token

    with time_machine.travel('2021-01-02 00:00:01'):
        with pytest.raises(Exception):
            user.decode_document_access_token(token)
