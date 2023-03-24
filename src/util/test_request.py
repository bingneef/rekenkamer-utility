import pytest


class MockRequest:
    def __init__(self, form, json):
        self.form = form
        self.json = json

    def get_json(self):
        return self.json


def test_request_form_form():
    from .request import get_post_body

    request = MockRequest(
        form={'foo': 'bar'},
        json=None
    )

    assert get_post_body(request) == {'foo': 'bar'}


def test_request_form_json():
    from .request import get_post_body

    request = MockRequest(
        form={},
        json={'foo': 'bar'}
    )
    assert get_post_body(request) == {'foo': 'bar'}


def test_verify_body_keys_mismatch_error():
    from .request import verify_body_keys

    with pytest.raises(Exception):
        verify_body_keys({'foo': 1}, ['bar'])


def test_verify_body_keys_partial_error():
    from .request import verify_body_keys

    with pytest.raises(Exception):
        verify_body_keys({'foo': 1}, ['foo', 'bar'])


def test_verify_body_keys_full_match():
    from .request import verify_body_keys

    # Assert no error is raised
    assert verify_body_keys({'foo': 1}, ['foo']) is None


def test_verify_body_keys_partial_match():
    from .request import verify_body_keys

    # Assert no error is raised
    assert verify_body_keys({'foo': 1, 'bar': 2}, ['foo']) is None
